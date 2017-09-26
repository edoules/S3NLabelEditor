all: lib_s3py/cyptnn.so

lib_s3py/cyptnn.so: lib_s3ptnn/cyptnn.so
	mv $< $@

lib_s3ptnn/cyptnn.so: \
	lib_s3ptnn/cyptnn.pyx \
	lib_s3ptnn/ptnn_algorithms.c 	lib_s3ptnn/ptnn_algorithms.h \
	lib_s3ptnn/ptnn_io.c 			lib_s3ptnn/ptnn_io.h \
	lib_s3ptnn/ptnn_newNode1.c 		lib_s3ptnn/ptnn_newNode1.h \
	lib_s3ptnn/ptnn_nodeLayer.c 	lib_s3ptnn/ptnn_nodeLayer.h \
	lib_s3ptnn/ptnn_train.c 		lib_s3ptnn/ptnn_train.h \
	lib_s3ptnn/ptnn_utility.c 		lib_s3ptnn/ptnn_utility.h \
	lib_s3ptnn/ptnn_weightLayer.c 	lib_s3ptnn/ptnn_weightLayer.h
	cd lib_s3ptnn; \
		python setup.py build_ext --inplace

clean:
	rm -f lib_s3py/*.pyc
	rm -f lib_s3py/*.so
	rm -f lib_s3ptnn/cyptnn.c
	rm -rf lib_s3ptnn/build

.PHONY: all clean
