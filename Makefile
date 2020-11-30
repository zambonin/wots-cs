CXXFLAGS = -O3 -Wall -std=c++17 -I include -Wno-unused-variable
LDFLAGS = -lbenchmark -lgmp -lcrypto -fopenmp
SHELL := /bin/bash
TARGETS := min-256 min-512 equal-256 equal-512 prob-256 prob-512

define SEARCH
params-$(TYPE).txt:
	python src/search-params.py $(subst -, ,$(TYPE)) >| $$@
endef

define GEN_CPP
bench-$(TYPE).cpp: params-$(TYPE).txt include/bytearray/include/bytearray.hpp
	python src/gen-cpp-bench.py $$< >| $$@
endef

define EXEC_CPP
raw-data-$(TYPE).txt: bench-$(TYPE)
	./$$< | tee $$@
endef

define PARSE_DATA
data-$(TYPE).txt: raw-data-$(TYPE).txt
	awk -f src/parse-encoding-time.awk $$< >| $$@
endef

define FIGURE
fig-$(TYPE).pdf: src/encoding-time.tex data-$(TYPE).txt
	latexmk -pdf -shell-escape -interaction=nonstopmode -jobname=fig-$(TYPE) \
		-pdflatex='pdflatex %O "\def\type{$(TYPE)}\input{%S}"' $$<
endef

help:
	@cat README

include/bytearray/include/bytearray.hpp:
	git submodule update --init include/bytearray
	sed -i 's/private/protected/' $@

src/xmss-reference/Makefile:
	git submodule update --init $(dir $@)
	sed -i '/CFLAGS /s/$$/ -fcommon/' $@

$(foreach TYPE,$(TARGETS),$(eval $(SEARCH)))
$(foreach TYPE,$(TARGETS),$(eval $(GEN_CPP)))
$(foreach TYPE,$(TARGETS),$(eval $(EXEC_CPP)))
$(foreach TYPE,$(TARGETS),$(eval $(PARSE_DATA)))
$(foreach TYPE,$(TARGETS),$(eval $(FIGURE)))

wots-tables: params-min-256.txt params-min-512.txt
	python src/filter-params.py

xmss-data: MAKEFLAGS = -j --no-print-directory -C src/xmss-reference
xmss-data: src/xmss-reference/Makefile
	$(foreach N,$(shell seq 1 128),\
		$(MAKE) $(MAKEFLAGS) benchmark_fast >| "data-tree-$(N).txt";)

data-xmss-256-512.txt:
	awk -f src/parse-xmss-cycles.awk data-tree-*.txt >| $@

xmss-table: data-xmss-256-512.txt
	python src/tree-comparison.py

clean:
	$(RM) params-*
	$(RM) bench-* raw-* data-*
	$(foreach TYPE,$(TARGETS),$(RM) fig-$(TYPE).pgf*;)
	$(foreach TYPE,$(TARGETS),latexmk -CA -f -silent fig-$(TYPE).pdf;)
	$(MAKE) -C src/xmss-reference clean
