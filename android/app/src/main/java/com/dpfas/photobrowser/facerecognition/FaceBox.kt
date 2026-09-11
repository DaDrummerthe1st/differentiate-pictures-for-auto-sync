package com.dpfas.photobrowser.facerecognition

/** One of YuNet's 5 facial landmarks (right eye, left eye, nose tip, right/left mouth corner). */
data class Landmark(val x: Float, val y: Float)

/** A detected face: bounding box + landmarks + confidence, in the coordinate space of whatever bitmap was passed to the detector. */
data class FaceBox(
    val left: Float,
    val top: Float,
    val width: Float,
    val height: Float,
    val score: Float,
    val landmarks: List<Landmark>,
) {
    fun scaledBy(scaleX: Float, scaleY: Float): FaceBox = copy(
        left = left * scaleX,
        top = top * scaleY,
        width = width * scaleX,
        height = height * scaleY,
        landmarks = landmarks.map { Landmark(it.x * scaleX, it.y * scaleY) },
    )
}
