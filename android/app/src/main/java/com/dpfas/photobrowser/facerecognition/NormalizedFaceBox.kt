package com.dpfas.photobrowser.facerecognition

/**
 * A [FaceBox] expressed as fractions (0..1) of the image it was detected on, rather than absolute
 * pixels. Lets a box be drawn correctly over a *different* decode of the same photo (the face
 * pipeline works on a downsampled analysis bitmap; the fullscreen viewer displays whatever
 * resolution Coil decoded) as long as both share the same aspect ratio, which they do - both are
 * EXIF-rotated decodes of the same source image.
 */
data class NormalizedFaceBox(val left: Float, val top: Float, val right: Float, val bottom: Float)

fun FaceBox.normalizedIn(imageWidth: Int, imageHeight: Int): NormalizedFaceBox = NormalizedFaceBox(
    left = left / imageWidth,
    top = top / imageHeight,
    right = (left + width) / imageWidth,
    bottom = (top + height) / imageHeight,
)
