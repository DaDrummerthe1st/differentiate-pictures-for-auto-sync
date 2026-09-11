package com.dpfas.photobrowser

import android.content.Context
import android.graphics.Bitmap
import android.os.Handler
import android.os.Looper
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.ImageView
import com.dpfas.photobrowser.facerecognition.FaceMatch
import com.dpfas.photobrowser.facerecognition.PhotoBitmapLoader
import com.dpfas.photobrowser.facerecognition.marginedCropRect

/**
 * Grid of cropped face thumbnails ranked by similarity to the tapped face. Crops off the main
 * thread with [PhotoBitmapLoader] + the same [marginedCropRect] logic the detection pipeline
 * already uses - not Coil (its 3.1.0 `ImageRequest.Builder` has no transformation-pipeline hook
 * to crop into, confirmed by inspecting the actual class - no point fighting that API gap for a
 * grid this size). Guards against GridView's view recycling racing a slow decode via the
 * ImageView's own tag, same technique any hand-rolled async-image-loading adapter needs.
 */
class SimilarFacesAdapter(
    private val context: Context,
    private val matches: List<FaceMatch>,
    private val loadImage: (ImageView, FaceMatch) -> Unit = { imageView, match ->
        imageView.setImageBitmap(null)
        imageView.tag = match
        val mainHandler = Handler(Looper.getMainLooper())
        Thread {
            val cropped = cropMatchedFace(context, match)
            mainHandler.post {
                if (imageView.tag === match) imageView.setImageBitmap(cropped)
            }
        }.start()
    },
) : BaseAdapter() {

    companion object {
        private const val CROP_MARGIN_RATIO = 0.3f

        fun cropMatchedFace(context: Context, match: FaceMatch): Bitmap? {
            val photo = PhotoBitmapLoader.load(context, match.uri) ?: return null
            val box = match.face.box
            val rect = marginedCropRect(
                left = box.left * photo.width,
                top = box.top * photo.height,
                right = box.right * photo.width,
                bottom = box.bottom * photo.height,
                marginRatio = CROP_MARGIN_RATIO,
                imageWidth = photo.width,
                imageHeight = photo.height,
            )
            return Bitmap.createBitmap(photo, rect.x, rect.y, rect.width, rect.height)
        }
    }

    override fun getCount() = matches.size

    override fun getItem(position: Int): FaceMatch = matches[position]

    override fun getItemId(position: Int) = position.toLong()

    override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
        val imageView = (convertView ?: LayoutInflater.from(context)
            .inflate(R.layout.grid_item_photo, parent, false)) as ImageView

        loadImage(imageView, matches[position])

        return imageView
    }
}
