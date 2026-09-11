package com.dpfas.photobrowser.facerecognition

import android.graphics.Bitmap

/** A detected face plus its embedding, ready to compare/cluster against other faces. */
data class FaceResult(val box: FaceBox, val embedding: FloatArray)

/**
 * Detects faces in a photo and embeds each one. No identity matching/clustering yet - that needs
 * a "who is this" UI and a place to store named entities, both out of scope for this pass (see
 * documentation/mobile/TODO.md).
 */
class FaceRecognitionPipeline(
    private val detector: FaceDetector,
    private val embedder: FaceEmbedder,
    private val marginRatio: Float = 0.2f,
) {

    fun scan(bitmap: Bitmap): List<FaceResult> =
        detector.detect(bitmap).map { box -> FaceResult(box, embedder.embed(cropFace(bitmap, box))) }

    /**
     * Axis-aligned crop with a margin, not a landmark-based similarity-transform alignment (the
     * standard ArcFace 5-point warp to a canonical pose) - a known simplification for this first
     * cut, flagged in documentation/mobile/TODO.md as a follow-up for embedding-quality accuracy.
     */
    private fun cropFace(bitmap: Bitmap, box: FaceBox): Bitmap {
        val rect = marginedCropRect(
            left = box.left,
            top = box.top,
            right = box.left + box.width,
            bottom = box.top + box.height,
            marginRatio = marginRatio,
            imageWidth = bitmap.width,
            imageHeight = bitmap.height,
        )
        return Bitmap.createBitmap(bitmap, rect.x, rect.y, rect.width, rect.height)
    }
}
