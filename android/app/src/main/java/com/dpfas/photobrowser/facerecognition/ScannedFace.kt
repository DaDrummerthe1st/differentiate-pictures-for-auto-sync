package com.dpfas.photobrowser.facerecognition

/** One detected face, as cached for reuse by the fullscreen overlay and similar-faces search. */
data class ScannedFace(val box: NormalizedFaceBox, val embedding: FloatArray) {
    // FloatArray doesn't have value equality by default - needed so cache/adapter tests can
    // compare ScannedFace instances by content instead of array reference.
    override fun equals(other: Any?): Boolean =
        this === other || (other is ScannedFace && box == other.box && embedding.contentEquals(other.embedding))

    override fun hashCode(): Int = 31 * box.hashCode() + embedding.contentHashCode()
}

fun FaceResult.toScannedFace(imageWidth: Int, imageHeight: Int): ScannedFace =
    ScannedFace(box.normalizedIn(imageWidth, imageHeight), embedding)
