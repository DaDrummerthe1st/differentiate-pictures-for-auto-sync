package com.dpfas.photobrowser.facerecognition

import android.net.Uri
import kotlin.math.sqrt

/** One face embedding compared against a query, matched to the photo it came from. */
data class FaceMatch(val uri: Uri, val face: ScannedFace, val similarity: Float)

object FaceSimilarity {

    fun cosineSimilarity(a: FloatArray, b: FloatArray): Float {
        var dot = 0f
        var normA = 0f
        var normB = 0f
        for (i in a.indices) {
            dot += a[i] * b[i]
            normA += a[i] * a[i]
            normB += b[i] * b[i]
        }
        val denominator = sqrt(normA) * sqrt(normB)
        return if (denominator == 0f) 0f else dot / denominator
    }

    /**
     * Ranks every face across [candidates] by similarity to [query], most similar first.
     * [excludeSelf], when given, is dropped from the results by reference - so the tapped face
     * doesn't trivially rank first against itself.
     */
    fun findSimilar(
        query: FloatArray,
        candidates: Map<Uri, List<ScannedFace>>,
        excludeSelf: ScannedFace? = null,
        topK: Int = 60,
    ): List<FaceMatch> =
        candidates.asSequence()
            .flatMap { (uri, faces) -> faces.asSequence().map { uri to it } }
            .filter { (_, face) -> face !== excludeSelf }
            .map { (uri, face) -> FaceMatch(uri, face, cosineSimilarity(query, face.embedding)) }
            .sortedByDescending { it.similarity }
            .take(topK)
            .toList()
}
