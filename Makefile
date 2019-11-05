CXXFLAGS = -O3 -Wall -std=c++17 -I include/wots/pqcrypto
LDFLAGS = -lbenchmark -lgmp -lcrypto
SHELL := /bin/bash
TARGETS := min-256 min-512 equal-256 equal-512

parse_results = \
	sed -e '1,3d; s/\s\+/ /g' $(1) \
	| paste -d\  - - - - - - \
	| awk -F"[><, ]" '{ \
			print $$3, $$7, $$5, $$9, $$12, $$28, $$44, $$60, $$76, $$92 \
		}' \
	| column -t

define SEARCH
params-$(TYPE).txt:
	python src/search-params.py $(subst -, ,$(TYPE)) >| params-$(TYPE).txt
endef

define GEN_CPP
bench-$(TYPE).cpp: params-$(TYPE).txt
	python src/gen-cpp-bench.py $(subst -, ,$(TYPE)) >| bench-$(TYPE).cpp
endef

define EXEC_CPP
data-$(TYPE).txt: bench-$(TYPE)
	./$$< >| raw-data-$(TYPE).txt
	$$(call parse_results,raw-data-$(TYPE).txt) >| data-$(TYPE).txt
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
	$(foreach TYPE,$(TARGETS),$(RM) fig-$(TYPE).pgf*;)
	$(foreach TYPE,$(TARGETS),latexmk -CA fig-$(TYPE).pdf;)
