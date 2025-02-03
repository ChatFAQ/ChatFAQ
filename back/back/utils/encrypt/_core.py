"""
Azor - the secret management solution to keep secrets safe
"""

import struct
import threading
from typing import Iterable, Mapping, Sequence

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from back.config import settings


def _encrypt(public_key: RSAPublicKey, data: bytes) -> list[bytes]:
    """
    Encrypts the given data using the public key.
    """

    padding_algorithm = padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA512()),
        algorithm=hashes.SHA512(),
        label=None,
    )
    max_chunk_size = get_max_message_size(public_key, padding_algorithm)

    chunks = [data[i : i + max_chunk_size] for i in range(0, len(data), max_chunk_size)]

    return [public_key.encrypt(chunk, padding_algorithm) for chunk in chunks]


def _decrypt(private_key: RSAPrivateKey, data: bytes) -> bytes:
    """
    Decrypts the given data using the private key.
    """

    return private_key.decrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA512()),
            algorithm=hashes.SHA512(),
            label=None,
        ),
    )


def get_max_message_size(public_key: RSAPublicKey, padding_algorithm) -> int:
    """
    The string needs to chunked into different parts to be encrypted. We detect
    here based on the key size what might be the maximum size of a chunk.
    By "detect" I mean for now we just hard-code it.
    """

    return 126


class LightBringer:
    """
    The class that holds the private key to encrypt and decrypt all the secrets
    found in the NissaString instances.

    Private key can be generated using the following command:

        openssl genpkey \
            -algorithm RSA \
            -out private_key.pem \
            -pkeyopt rsa_keygen_bits:4096
    """

    def __init__(self, private_key_pem: str):
        self.private_key: RSAPrivateKey = serialization.load_pem_private_key(
            private_key_pem.encode("utf-8"),
            password=None,
            backend=default_backend(),
        )
        self.public_key: RSAPublicKey = self.private_key.public_key()

    def ensure_nissa(self, value: "str | NissaString") -> "NissaString":
        """
        Ensures that the given object is a NissaString and returns it. If it's
        a string, it's converted to a NissaString using the LightBringer
        instance.
        """

        if isinstance(value, NissaString):
            return value
        else:
            return self.securize(value)

    def null_nissa(self) -> "NissaString":
        """
        Returns a NULL string, which is a NissaString without any bits but with
        the public key.
        """

        return NissaString([], self.public_key)

    def securize(self, value: str) -> "NissaString":
        """
        Encrypts the given string and returns a NissaString instance that can
        be used to decrypt it later.
        """

        return NissaString(
            bits=_encrypt(self.public_key, value.encode("utf-8")),
            public_key=self.public_key,
        )


class DecryptedNissaString(str):
    pass


def blur_decrypted_nissa(value: object) -> object:
    """
    Recursively scans a JSON-serializable object and blurs the parts of it that
    were decrypted by the LightBringer.
    """

    if isinstance(value, DecryptedNissaString):
        return "*****"
    elif isinstance(value, (str, bytes)):
        return value
    elif isinstance(value, Mapping):
        return {k: blur_decrypted_nissa(v) for k, v in value.items()}
    elif isinstance(value, Sequence):
        return [blur_decrypted_nissa(x) for x in value]
    else:
        return value


class NissaString:
    """
    Represents a secret that needs to be kept safe. To decrypt it, pass
    LightBringer through its heart.
    """

    def __init__(self, bits: list[bytes], public_key: RSAPublicKey):
        self.bits = bits
        self.public_key = public_key

    @property
    def is_null(self) -> bool:
        """
        Returns True if we hold no bits, meaning that the secret is NULL.
        """

        return not self.bits

    def to_bytes(self) -> bytes:
        # Serialize public key
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        # Pack the number of bits and the length of the public key
        header = struct.pack("!II", len(self.bits), len(public_bytes))

        # Pack each bit's length and content
        bits_data = b""
        for bit in self.bits:
            bits_data += struct.pack("!I", len(bit)) + bit

        # Combine all parts
        return header + bits_data + public_bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> "NissaString":
        # Unpack the header
        bits_count, public_key_length = struct.unpack("!II", data[:8])

        # Extract bits
        offset = 8
        bits = []
        for _ in range(bits_count):
            bit_length = struct.unpack("!I", data[offset : offset + 4])[0]
            offset += 4
            bits.append(data[offset : offset + bit_length])
            offset += bit_length

        # Extract and load the public key
        public_key_bytes = data[offset : offset + public_key_length]
        public_key = serialization.load_der_public_key(public_key_bytes)

        return cls(bits, public_key)

    def from_other(self, other: "NissaString | str") -> "NissaString":
        """
        Ensures that the given object is a NissaString and returns it. If it's
        a string, it's converted to a NissaString using the LightBringer
        instance.
        """

        if isinstance(other, NissaString):
            return other
        else:
            return NissaString(
                _encrypt(self.public_key, other.encode("utf-8")), self.public_key
            )

    def decrypt(self, lb: LightBringer) -> str:
        """
        Decrypts the secret and returns it as a string.
        """

        return DecryptedNissaString(
            b"".join(_decrypt(lb.private_key, bit) for bit in self.bits).decode("utf-8")
        )

    def __repr__(self):
        return f"NissaString(***)"

    def __add__(self, other):
        return NissaString(
            [*self.bits, *self.from_other(other).bits],
            self.public_key,
        )

    def __radd__(self, other):
        return NissaString(
            [*self.from_other(other).bits, *self.bits],
            self.public_key,
        )

    def join(self, others: Iterable["str | NissaString"]) -> "NissaString":
        """
        Like str's join(), but ends up with a NissaString instance.
        """

        others = [self.from_other(o) for o in others]
        bits = [b for o in others[:1] for b in o.bits]

        for o in others[1:]:
            bits.extend(self.bits)
            bits.extend(o.bits)

        return NissaString(bits, self.public_key)


_light_bringer: LightBringer | None = None
_light_bringer_lock = threading.Lock()


def get_light_bringer() -> LightBringer:
    """
    Gets the global LightBringer instance.
    """

    global _light_bringer

    if _light_bringer is None:
        with _light_bringer_lock:
            if _light_bringer is None:
                _light_bringer = LightBringer(settings.AZOR_PRIVATE_KEY)

    return _light_bringer
