
# TODO lib directory could be changed to /usr/local/lib

VERSION=1.0.0

all: debs

debs: libsai-dev_$(VERSION)_amd64.deb libsai_$(VERSION)_amd64.deb

libsai-dev_$(VERSION)_amd64.deb: ../SAI/inc/*.h ../SAI/experimental/*.h
	mkdir -p -m 755 libsai-dev_$(VERSION)_amd64/usr/include/sai
	find -type d |xargs chmod go-w
	install -vCD -m 644 ../SAI/inc/*.h libsai-dev_$(VERSION)_amd64/usr/include/sai/
	install -vCD -m 644 ../SAI/experimental/*.h libsai-dev_$(VERSION)_amd64/usr/include/sai/
	cd libsai-dev_$(VERSION)_amd64 && find usr -type f | xargs md5sum > DEBIAN/md5sums
	dpkg-deb --build --root-owner-group libsai-dev_$(VERSION)_amd64

libsai_$(VERSION)_amd64.deb: ../lib/libsai.so
	mkdir -p -m 755 libsai_$(VERSION)_amd64/etc/dash
	install -vCD ../../bmv2/dash_pipeline.bmv2/* libsai_$(VERSION)_amd64/etc/dash/
	mkdir -p -m 755 libsai_$(VERSION)_amd64/usr/lib/x86_64-linux-gnu/
	find -type d |xargs chmod go-w
	install -vCD ../lib/libsai.so libsai_$(VERSION)_amd64/usr/lib/x86_64-linux-gnu/libsai.so
	cd libsai_$(VERSION)_amd64 && find usr -type f | xargs md5sum > DEBIAN/md5sums
	dpkg-deb --build --root-owner-group libsai_$(VERSION)_amd64

.PHONY: clean

clean:
	rm -f *.deb */DEBIAN/md5sums
	rm -rf libsai_$(VERSION)_amd64/usr libsai-dev_$(VERSION)_amd64/usr
