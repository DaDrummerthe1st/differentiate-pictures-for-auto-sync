package com.dpfas.photobrowser.facerecognition

import kotlin.math.max
import kotlin.math.min
import kotlin.math.roundToInt

data class CropRect(val x: Int, val y: Int, val width: Int, val height: Int)

/**
 * A `[left, top, right, bottom]` pixel rect expanded by [marginRatio] on each side, then clamped
 * to `[0, imageWidth) x [0, imageHeight)`. Shared by [FaceRecognitionPipeline] (cropping a face for
 * embedding) and [FaceCropTransformation] (cropping a face thumbnail for display) so both use the
 * same clamping behavior.
 */
fun marginedCropRect(
    left: Float,
    top: Float,
    right: Float,
    bottom: Float,
    marginRatio: Float,
    imageWidth: Int,
    imageHeight: Int,
): CropRect {
    val marginX = (right - left) * marginRatio
    val marginY = (bottom - top) * marginRatio

    val clampedLeft = (left - marginX).coerceIn(0f, imageWidth.toFloat())
    val clampedTop = (top - marginY).coerceIn(0f, imageHeight.toFloat())
    val clampedRight = (right + marginX).coerceIn(0f, imageWidth.toFloat())
    val clampedBottom = (bottom + marginY).coerceIn(0f, imageHeight.toFloat())

    val width = max(1, (clampedRight - clampedLeft).roundToInt())
    val height = max(1, (clampedBottom - clampedTop).roundToInt())
    val x = min(clampedLeft.roundToInt(), imageWidth - width).coerceAtLeast(0)
    val y = min(clampedTop.roundToInt(), imageHeight - height).coerceAtLeast(0)

    return CropRect(x, y, width, height)
}
