DIST  = dist
PYZ   = $(DIST)/seth.pyz
STAGE = $(DIST)/_stage
SRCS  = $(shell find seth -name "*.py")

.PHONY: pyz clean

pyz: $(PYZ)

$(PYZ): $(SRCS)
	@mkdir -p $(STAGE)
	@cp -r seth $(STAGE)/
	python3 -m zipapp $(STAGE) \
	    --main "seth.cli:main" \
	    --python "/usr/bin/env python3" \
	    --output $(PYZ)
	@rm -rf $(STAGE)
	@chmod +x $(PYZ)
	@echo "Built $(PYZ)  ($$(wc -c < $(PYZ)) bytes)"

clean:
	rm -rf $(DIST)
