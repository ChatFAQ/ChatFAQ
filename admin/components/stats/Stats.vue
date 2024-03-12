<template>
    <div class="dashboard-page-title">{{ $t("stats") }}</div>
    <div class="stats-wrapper" v-loading="itemsStore.loading" element-loading-background="rgba(255, 255, 255, 0.8)">
        <div class="text-explanation" v-html="$t('statsexplanation')"></div>
        <Filters :filtersSchema="filterSchema"/>
        <div class="stats" v-if="stats">
            <div class="section-title">Conversations</div>
            <div class="group-stats">
                <StatCard :title="$t('totalconversations')" :content="stats.total_conversations"/>
                <StatCard :title="$t('conversationsmessagecount')" :content="stats.conversations_message_count"/>
                <StatCard :title="$t('conversationsbydate')" :content="stats.conversations_by_date"/>
                <StatCard :title="$t('chitchatscount')" :content="stats.chit_chats_count"/>
                <StatCard type="percentage" :title="$t('chitchatspercentage')" :content="stats.chit_chats_percentage"/>
            </div>
            <div class="section-title">Messages</div>
            <div class="group-stats">
                <StatCard :title="$t('chitchatscount')" :content="stats.chit_chats_count"/>
                <StatCard type="percentage" :title="$t('chitchatspercentage')" :content="stats.chit_chats_percentage"/>
                <StatCard :title="$t('unanswerablequeriescount')" :content="stats.unanswerable_queries_count"/>
                <StatCard type="percentage" :title="$t('unanswerablequeriespercentage')" :content="stats.unanswerable_queries_percentage"/>
                <StatCard :title="$t('answerablequeriescount')" :content="stats.answerable_queries_count"/>
                <StatCard type="percentage" :title="$t('answerablequeriespercentage')" :content="stats.answerable_queries_percentage"/>
            </div>
            <div class="section-title">Reviews & Feedback</div>
            <div class="group-stats">
                <StatCard :title="$t('precision')" :content="stats.precision"/>
                <StatCard :title="$t('recall')" :content="stats.recall"/>
                <StatCard :title="$t('f1')" :content="stats.f1"/>
                <StatCard :title="$t('adminquality')" :content="stats.admin_quality"/>
                <StatCard :title="$t('userquality')" :content="stats.user_quality"/>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import {useItemsStore} from "~/store/items.js";
import Filters from "~/components/generic/filters/Filters.vue";
import {useI18n} from "vue-i18n";
import StatCard from "~/components/stats/StatCard.vue";

const { t } = useI18n();
const itemsStore = useItemsStore()
const {$axios} = useNuxtApp();
const stats = ref(undefined)

const filterSchema = ref(
   [
       {'type': 'ref', 'placeholder': t('rag'), 'field': 'rag', 'endpoint': '/back/api/language-model/rag-configs/'},
       {'type': 'range-date', 'startPlaceholder': t('startdate'), 'endPlaceholder': t('enddate'), 'field': 'created_date'},
   ]
)
watch(() => itemsStore.filters, async () => {  // For when setting filters from outside
    await requestStats()
}, {deep: true})

async function requestStats() {
    if (itemsStore.filters.rag === undefined)
        stats.value = undefined

    let filters = {...itemsStore.filters}
    if (filters.created_date__gte) {
        filters.min_date = filters.created_date__gte
        delete filters.created_date__gte
    } else {
        filters.min_date = undefined
    }
    if (filters.created_date__lte) {
        filters.max_date = filters.created_date__lte
        delete filters.created_date__lte
    } else {
        filters.max_date = undefined
    }

    const response = await $axios.get('/back/api/broker/stats/', {params: filters})
    stats.value = response.data
}

</script>

<style lang="scss">
</style>

<style lang="scss" scoped>
.stats-wrapper {
    display: flex;
    flex-wrap: wrap;
    margin-left: 160px;
    margin-right: 160px;
    max-width: 1300px;
    margin-top: 32px;
    .stats {
        width: 100%;
        margin-left: 16px;
        margin-right: 16px;
        margin-top: 26px;
        .section-title {

            //styleName: Body/SM/SemiBold;
            font-family: Open Sans;
            font-size: 14px;
            font-weight: 600;
            line-height: 20px;
            letter-spacing: 0em;
            text-align: left;
            color: #020C1C;
            margin-bottom: 16px;
            margin-top: 26px;
        }
        .group-stats {
            display: grid;
            flex-wrap: wrap;
            width: 100%;
            justify-items: stretch;
            grid-template-columns: repeat(auto-fill, 400px);
            gap: 16px 32px;
        }
    }
}

.text-explanation {
    margin-right: 16px;
    margin-left: 16px;
    font-size: 14px;
    font-weight: 400;
    line-height: 20px;
    padding-left: 18px;
    border-left: 2px solid $chatfaq-color-primary-500;

}
</style>
