.PHONY: test build-cpp demo generate clean

test:
	./scripts/test.sh

build-cpp:
	./scripts/build_cpp.sh

demo:
	./scripts/run_demo.sh

generate:
	./scripts/generate_demo.sh

clean:
	find src tests -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf build
