"""
Given a list of questions and a list of contents, this script computes the similarity between each question and each content ussing a cross encoder.
The cross encoder is a transformer model that takes a pair of sentences and outputs a score between 0 and 1 indicating how similar the sentences are.
If the score is greater than 0.5, the question is considered answerable.
The goal of this script is to get the number of answerable questions and the percentage of answerable questions given a list of contents.
"""
import argparse
import pandas as pd
import numpy as np
import torch
from sentence_transformers import CrossEncoder
from tqdm import tqdm
import os

def get_answerable_questions(contents_path, questions_path, language, device, batch_size, max_questions=None):
    if language == 'en':
        model_name = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
    else:
        model_name = 'nreimers/mmarco-mMiniLMv2-L6-H384-v1'

    model = CrossEncoder(model_name, max_length=512, device=device)
    model.model = torch.compile(model.model, mode='default')

    df = pd.read_csv(contents_path)
    df_q = pd.read_csv(questions_path)

    # sample questions if max_questions is specified
    if max_questions is not None:
        df_q = df_q.sample(max_questions, random_state=42)

    contents = df['content'].tolist()
    questions = df_q['question'].tolist()

    progress_file = questions_path.replace('.csv', '_answerable.npy')
    start_index = 0

    # Check if previous progress exists
    if os.path.exists(progress_file):
        progress_data = np.load(progress_file, allow_pickle=True)
        start_index, scores = progress_data[0], progress_data[1]
    else:
        scores = np.zeros((len(questions), len(contents)))

    len_q = len(questions)
    for i in tqdm(range(start_index, len_q, batch_size)):
        batch_questions = questions[i:i+batch_size]
        pairs = [[q, c] for q in batch_questions for c in contents]
        result = model.predict(pairs, activation_fct=torch.sigmoid)
        result = result.reshape(len(batch_questions), len(contents))
        scores[i:i+batch_size] = result
        np.save(progress_file, np.array([i + batch_size, scores], dtype=object))  # Save current index and scores
        torch.cuda.empty_cache()

    # Post-processing
    df_q['score'] = scores.max(axis=1)
    df_q['answerable'] = df_q['score'] > 0.5
    df_q_path = questions_path.replace('.csv', '_answerable.parquet')
    df_q.to_parquet(df_q_path)

    # remove progress file
    os.remove(progress_file)

    answerable_questions = df_q['answerable'].sum()
    return answerable_questions, answerable_questions / len(df_q)

def main():
    parser = argparse.ArgumentParser(description='Process content and question files to find answerable questions.')
    parser.add_argument('contents_path', type=str, help='Path to the contents CSV file')
    parser.add_argument('questions_path', type=str, help='Path to the questions CSV file')
    parser.add_argument('--lang', type=str, default='en', help='Language of the contents and questions')
    parser.add_argument('--device', type=str, default='cpu', choices=['cuda', 'cpu'], help='Device to run the model on (cuda or cpu)')
    parser.add_argument('--batch_size', type=int, default=4, help='Batch size for processing')
    # add a max_questions argument to limit the number of questions to process, if not specified, process all questions
    parser.add_argument('--max_questions', type=int, default=None, help='Max number of questions to process')

    args = parser.parse_args()

    answerable_count, answerable_percentage = get_answerable_questions(
        args.contents_path, args.questions_path, args.lang, args.device, args.batch_size, args.max_questions)

    print(f"Number of answerable questions: {answerable_count}")
    print(f"Percentage of answerable questions: {answerable_percentage:.2f}")

if __name__ == '__main__':
    main()

