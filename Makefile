CXXFLAGS = -O3 -Wall -std=c++17 -I include -Wno-unused-variable
LDFLAGS = -lbenchmark -lgmp -lcrypto -fopenmp
SHELL := /bin/bash
TARGETS := min-256 min-512 equal-256 equal-512 prob-256 prob-512

define SEARCH
params-$(TYPE).txt:
	python src/search-params.py $(subst -, ,$(TYPE)) >| params-$(TYPE).txt
endef

define GEN_CPP
bench-$(TYPE).cpp: params-$(TYPE).txt
	python src/gen-cpp-bench.py params-$(TYPE).txt >| bench-$(TYPE).cpp
	sed -i 's/private/protected/' include/bytearray/include/bytearray.hpp
endef

define EXEC_CPP
data-$(TYPE).txt: bench-$(TYPE)
	./$$< | tee raw-data-$(TYPE).txt
	awk -f src/parse-encoding-time.awk raw-data-$(TYPE).txt >| data-$(TYPE).txt
endef

define FIGURE
fig-$(TYPE).pdf: src/encoding-time.tex data-$(TYPE).txt
	latexmk -pdf -shell-escape -interaction=nonstopmode -jobname=fig-$(TYPE) \
		-pdflatex='pdflatex %O "\def\type{$(TYPE)}\input{%S}"' $$<
endef

help:
	@less README

$(foreach TYPE,$(TARGETS),$(eval $(SEARCH)))
$(foreach TYPE,$(TARGETS),$(eval $(GEN_CPP)))
$(foreach TYPE,$(TARGETS),$(eval $(EXEC_CPP)))
$(foreach TYPE,$(TARGETS),$(eval $(FIGURE)))

tables: params-min-256.txt params-min-512.txt
	python src/filter-params.py

clean:
	$(RM) params-*
	$(RM) bench-* raw-* data-*
	sed -i 's/protected/private/' include/bytearray/include/bytearray.hpp
	$(foreach TYPE,$(TARGETS),$(RM) fig-$(TYPE).pgf*;)
	$(foreach TYPE,$(TARGETS),latexmk -CA fig-$(TYPE).pdf;)
