.PHONY: test build-cpp demo generate clean

test:
	bash ./scripts/test.sh

build-cpp:
	bash ./scripts/build_cpp.sh

demo:
	bash ./scripts/run_demo.sh

generate:
	bash ./scripts/generate_demo.sh

clean:
	find src tests -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf build
