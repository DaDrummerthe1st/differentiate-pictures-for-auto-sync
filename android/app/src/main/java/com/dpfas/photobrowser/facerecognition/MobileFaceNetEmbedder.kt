package com.dpfas.photobrowser.facerecognition

import ai.onnxruntime.OnnxTensor
import android.content.Context
import android.graphics.Bitmap
import ai.onnxruntime.OrtEnvironment
import java.nio.FloatBuffer

/**
 * MobileFaceNet (ArcFace) face embedder, running the raw vendored ONNX graph directly via ONNX
 * Runtime Mobile (see `assets/models/LICENSES.md`). Preprocessing (112x112, RGB channel order,
 * (pixel-127.5)/127.5 normalization) is verified against the model's own training/inference
 * source (`deepinsight/insightface`'s `recognition/arcface_torch/inference.py`), not assumed -
 * see LICENSES.md for the exact check. Outputs a 512-d embedding.
 */
class MobileFaceNetEmbedder(context: Context) : FaceEmbedder {

    companion object {
        private const val INPUT_SIZE = 112
        private const val INPUT_NAME = "data"
        private const val MEAN = 127.5f
        private const val STD = 127.5f
    }

    private val env: OrtEnvironment = OrtEnvironment.getEnvironment()
    private val session = env.createSession(readModelAsset(context, "arcface_mobilefacenet.onnx"))

    override fun embed(faceCrop: Bitmap): FloatArray {
        val scaled = Bitmap.createScaledBitmap(faceCrop, INPUT_SIZE, INPUT_SIZE, true)

        bitmapToRgbNormalizedTensor(scaled).use { inputTensor ->
            session.run(mapOf(INPUT_NAME to inputTensor)).use { outputs ->
                val tensor = outputs.iterator().next().value as OnnxTensor
                val out = FloatArray(tensor.floatBuffer.remaining())
                tensor.floatBuffer.get(out)
                return out
            }
        }
    }

    /** NCHW, RGB channel order, (pixel-127.5)/127.5 normalization - see class doc comment. */
    private fun bitmapToRgbNormalizedTensor(bitmap: Bitmap): OnnxTensor {
        val w = bitmap.width
        val h = bitmap.height
        val pixels = IntArray(w * h)
        bitmap.getPixels(pixels, 0, w, 0, 0, w, h)

        val channelSize = w * h
        val data = FloatArray(3 * channelSize)
        for (i in 0 until channelSize) {
            val p = pixels[i]
            data[i] = (((p shr 16) and 0xFF).toFloat() - MEAN) / STD // R
            data[channelSize + i] = (((p shr 8) and 0xFF).toFloat() - MEAN) / STD // G
            data[2 * channelSize + i] = ((p and 0xFF).toFloat() - MEAN) / STD // B
        }
        return OnnxTensor.createTensor(env, FloatBuffer.wrap(data), longArrayOf(1, 3, h.toLong(), w.toLong()))
    }
}
