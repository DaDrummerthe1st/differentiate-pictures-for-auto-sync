package com.dpfas.photobrowser.facerecognition

import ai.onnxruntime.OnnxTensor
import ai.onnxruntime.OrtEnvironment
import ai.onnxruntime.OrtSession
import android.content.Context
import android.graphics.Bitmap
import java.nio.FloatBuffer

/**
 * YuNet face detector, running the raw vendored ONNX graph directly via ONNX Runtime Mobile (see
 * `assets/models/LICENSES.md`). Preprocessing (fixed 640x640 input, BGR channel order, no pixel
 * normalization) and output decoding both mirror OpenCV's own C++ `FaceDetectorYNImpl` exactly -
 * see [YuNetDecoder]'s doc comment for the source this was ported from.
 */
class YuNetFaceDetector(
    context: Context,
    private val scoreThreshold: Float = 0.6f,
    private val nmsThreshold: Float = 0.3f,
    private val topK: Int = 50,
) : FaceDetector {

    companion object {
        private const val INPUT_SIZE = 640
        private const val INPUT_NAME = "input"
    }

    private val env: OrtEnvironment = OrtEnvironment.getEnvironment()
    private val session: OrtSession = env.createSession(readModelAsset(context, "face_detection_yunet_2023mar.onnx"))

    override fun detect(bitmap: Bitmap): List<FaceBox> {
        if (bitmap.width <= 0 || bitmap.height <= 0) return emptyList()

        val scaled = Bitmap.createScaledBitmap(bitmap, INPUT_SIZE, INPUT_SIZE, true)
        val allBoxes = mutableListOf<FaceBox>()

        bitmapToBgrTensor(scaled).use { inputTensor ->
            session.run(mapOf(INPUT_NAME to inputTensor)).use { outputs ->
                for (stride in YuNetDecoder.STRIDES) {
                    val cols = INPUT_SIZE / stride
                    val rows = INPUT_SIZE / stride
                    val cls = readOutput(outputs, "cls_$stride", cols * rows)
                    val obj = readOutput(outputs, "obj_$stride", cols * rows)
                    val bbox = readOutput(outputs, "bbox_$stride", cols * rows * 4)
                    val kps = readOutput(outputs, "kps_$stride", cols * rows * 10)
                    allBoxes += YuNetDecoder.decodeLevel(stride, cols, rows, cls, obj, bbox, kps, scoreThreshold)
                }
            }
        }

        val kept = YuNetDecoder.nms(allBoxes, nmsThreshold, topK)
        val scaleX = bitmap.width.toFloat() / INPUT_SIZE
        val scaleY = bitmap.height.toFloat() / INPUT_SIZE
        return kept.map { it.scaledBy(scaleX, scaleY) }
    }

    private fun readOutput(outputs: OrtSession.Result, name: String, size: Int): FloatArray {
        val tensor = outputs.get(name).get() as OnnxTensor
        val out = FloatArray(size)
        tensor.floatBuffer.get(out)
        return out
    }

    /** NCHW, BGR channel order, raw 0-255 pixel values - matches `cv::dnn::blobFromImage`'s defaults (no mean/scale, no RGB swap) used by OpenCV's own YuNet wrapper. */
    private fun bitmapToBgrTensor(bitmap: Bitmap): OnnxTensor {
        val w = bitmap.width
        val h = bitmap.height
        val pixels = IntArray(w * h)
        bitmap.getPixels(pixels, 0, w, 0, 0, w, h)

        val channelSize = w * h
        val data = FloatArray(3 * channelSize)
        for (i in 0 until channelSize) {
            val p = pixels[i]
            data[i] = (p and 0xFF).toFloat() // B
            data[channelSize + i] = ((p shr 8) and 0xFF).toFloat() // G
            data[2 * channelSize + i] = ((p shr 16) and 0xFF).toFloat() // R
        }
        return OnnxTensor.createTensor(env, FloatBuffer.wrap(data), longArrayOf(1, 3, h.toLong(), w.toLong()))
    }
}
