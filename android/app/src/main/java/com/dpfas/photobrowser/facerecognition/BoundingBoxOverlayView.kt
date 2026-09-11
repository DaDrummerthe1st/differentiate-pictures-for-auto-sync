package com.dpfas.photobrowser.facerecognition

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Matrix
import android.graphics.Paint
import android.graphics.RectF
import android.util.AttributeSet
import android.view.GestureDetector
import android.view.MotionEvent
import android.view.View

/**
 * Draws [ScannedFace] boxes over a photo, in the fullscreen viewer only - "subtle, concealable"
 * per documentation/tags/UX_FLOWS.md's existing box-level design, and deliberately not drawn in
 * the grid per documentation/mobile/UX_FLOWS.md's "badge, not drawn boxes" decision. Tapping a box
 * fires [onFaceTapped]; a touch that starts outside every box is left alone so the PhotoView
 * underneath still gets pan/zoom/swipe gestures.
 */
class BoundingBoxOverlayView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
) : View(context, attrs) {

    /** The size (in pixels) of the image these boxes are normalized against - needed to convert fractions back to image-space before applying [imageMatrix]. */
    var imageSize: Pair<Int, Int>? = null
        set(value) { field = value; invalidate() }

    var faces: List<ScannedFace> = emptyList()
        set(value) { field = value; invalidate() }

    /** Maps image-space coordinates to this view's coordinates - typically a PhotoView's current (possibly zoomed/panned) display matrix. */
    var imageMatrix: Matrix? = null
        set(value) { field = value; invalidate() }

    var onFaceTapped: ((ScannedFace) -> Unit)? = null

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 4f
        color = Color.argb(180, 255, 255, 255)
    }

    private val gestureDetector = GestureDetector(
        context,
        object : GestureDetector.SimpleOnGestureListener() {
            override fun onSingleTapUp(e: MotionEvent): Boolean {
                hitTest(e.x, e.y)?.let { onFaceTapped?.invoke(it) }
                return true
            }
        },
    )

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val (imageWidth, imageHeight) = imageSize ?: return
        val matrix = imageMatrix ?: return
        for (face in faces) {
            canvas.drawRect(boxToViewRect(face.box, imageWidth, imageHeight, matrix), paint)
        }
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        if (event.actionMasked == MotionEvent.ACTION_DOWN && hitTest(event.x, event.y) == null) {
            return false // outside every box - let the view underneath (PhotoView) handle it
        }
        gestureDetector.onTouchEvent(event)
        return true
    }

    private fun hitTest(x: Float, y: Float): ScannedFace? {
        val (imageWidth, imageHeight) = imageSize ?: return null
        val matrix = imageMatrix ?: return null
        return findTappedFace(faces, x, y, imageWidth, imageHeight, matrix)
    }

    companion object {
        /** Pure mapping logic, split out for testability without a real Canvas/View. */
        fun boxToViewRect(box: NormalizedFaceBox, imageWidth: Int, imageHeight: Int, matrix: Matrix): RectF {
            val rect = RectF(
                box.left * imageWidth,
                box.top * imageHeight,
                box.right * imageWidth,
                box.bottom * imageHeight,
            )
            matrix.mapRect(rect)
            return rect
        }

        /** Pure hit-test logic, split out for testability without a real touch dispatch. */
        fun findTappedFace(faces: List<ScannedFace>, x: Float, y: Float, imageWidth: Int, imageHeight: Int, matrix: Matrix): ScannedFace? =
            faces.firstOrNull { boxToViewRect(it.box, imageWidth, imageHeight, matrix).contains(x, y) }
    }
}
