package com.dpfas.photobrowser

import android.net.Uri
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import androidx.recyclerview.widget.RecyclerView
import com.dpfas.photobrowser.facerecognition.BoundingBoxOverlayView
import com.dpfas.photobrowser.facerecognition.FaceScanCache
import com.dpfas.photobrowser.facerecognition.ScannedFace
import io.getstream.photoview.PhotoView

/**
 * Backs the swipeable fullscreen [androidx.viewpager2.widget.ViewPager2], one photo per page.
 * Detected-face boxes are opt-in via [showFaceBoxes] (off by default) - never shown in the grid,
 * per documentation/mobile/UX_FLOWS.md's "badge, not drawn boxes" decision for that screen.
 * Tapping a box invokes [onFaceTapped] (only reachable when [showFaceBoxes] is on, since the
 * overlay itself is GONE otherwise and receives no touches).
 */
class FullscreenPhotoPagerAdapter(
    private val photoUris: List<Uri>,
    private val loadImage: (ImageView, Uri) -> Unit,
    private val onFaceTapped: (ScannedFace) -> Unit = {},
) : RecyclerView.Adapter<FullscreenPhotoPagerAdapter.ViewHolder>() {

    var showFaceBoxes: Boolean = false
        set(value) {
            field = value
            notifyDataSetChanged()
        }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val photoView: PhotoView = itemView.findViewById(R.id.fullscreen_photo)
        val overlay: BoundingBoxOverlayView = itemView.findViewById(R.id.face_box_overlay)
    }

    override fun getItemCount() = photoUris.size

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val itemView = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_fullscreen_photo, parent, false)
        return ViewHolder(itemView)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val uri = photoUris[position]
        loadImage(holder.photoView, uri)
        bindFaceBoxes(holder, uri)
    }

    /**
     * Boxes are normalized (0..1), so they need the *displayed* drawable's intrinsic size to
     * convert back to pixels before the PhotoView's own display matrix (zoom/pan) is applied -
     * both are only known once Coil's image has actually loaded, which is exactly when PhotoView
     * itself recalculates and reports its matrix, so that single listener covers both.
     */
    private fun bindFaceBoxes(holder: ViewHolder, uri: Uri) {
        holder.overlay.visibility = if (showFaceBoxes) View.VISIBLE else View.GONE
        holder.overlay.faces = FaceScanCache.get(uri) ?: emptyList()
        holder.overlay.onFaceTapped = onFaceTapped
        holder.photoView.setOnMatrixChangeListener {
            holder.overlay.imageMatrix = holder.photoView.imageMatrix
            holder.photoView.drawable?.let { drawable ->
                holder.overlay.imageSize = drawable.intrinsicWidth to drawable.intrinsicHeight
            }
        }
    }
}
