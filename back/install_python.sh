#!/bin/bash

set -eux

cd /root

PYTHON_VERSION="$(curl -s 'https://www.python.org/ftp/python/' | sed -E 's/.*<a href="[^"]*">([^<]*)\/.*/\1/' | grep "^${PYTHON_MAJOR_VERSION}" | sort -V | tail -n 1)"
export PYTHON_VERSION

curl "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz" -o python.tar.xz
curl "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz.asc" -o python.tar.xz.asc

GNUPGHOME="$(mktemp -d)"
export GNUPGHOME

gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys "$GPG_KEY"
gpg --batch --verify python.tar.xz.asc python.tar.xz

command -v gpgconf > /dev/null && gpgconf --kill all || :

rm -rf "$GNUPGHOME" python.tar.xz.asc
mkdir -p /usr/src/python
tar --extract --directory /usr/src/python --strip-components=1 --file python.tar.xz
rm python.tar.xz

cd /usr/src/python
gnuArch="$(dpkg-architecture --query DEB_BUILD_GNU_TYPE)"
./configure \
    --build="$gnuArch" \
    --enable-loadable-sqlite-extensions \
    --enable-optimizations \
    --enable-option-checking=fatal \
    --enable-shared \
    --with-lto \
    --with-system-expat

nproc="$(nproc)"
make -j "$nproc"
make install

# enable GDB to load debugging data: https://github.com/docker-library/python/pull/701
bin="$(readlink -ve /usr/local/bin/python3)"
dir="$(dirname "$bin")"
mkdir -p "/usr/share/gdb/auto-load/$dir"
cp -vL Tools/gdb/libpython.py "/usr/share/gdb/auto-load/$bin-gdb.py"

cd /
rm -rf /usr/src/python

find /usr/local -depth \
    \( \
        \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
        -o \( -type f -a \( -name '*.pyc' -o -name '*.pyo' -o -name 'libpython*.a' \) \) \
    \) -exec rm -rf '{}' +

ldconfig

python3 --version

# for src in idle3 pydoc3 python3 python3-config; do \
#     dst="$(echo "$src" | tr -d 3)"; \
#     [ -s "/usr/local/bin/$src" ]; \
#     [ ! -e "/usr/local/bin/$dst" ]; \
#     ln -svT "$src" "/usr/local/bin/$dst"; \
# done
