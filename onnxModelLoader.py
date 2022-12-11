import onnx
import onnxoptimizer

onnx_model = onnx.load("Resources/OnnxFile/ultra_light_640.onnx")
passes = ["extract_constant_to_initializer", "eliminate_unused_initializer"]
optimized_model = onnxoptimizer.optimize(onnx_model, passes)

onnx.save(optimized_model, "Resources/OnnxFile/ultra_light_640.onnx")

