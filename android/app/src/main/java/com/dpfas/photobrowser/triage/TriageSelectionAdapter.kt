package com.dpfas.photobrowser.triage

import android.content.Context
import android.net.Uri
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.CheckBox
import android.widget.ImageView
import coil3.load
import coil3.size.Precision
import com.dpfas.photobrowser.R

/** Option A demo's grid: same thumbnails as the real grid, plus a checkbox badge reflecting [TriageSelection]. */
class TriageSelectionAdapter(
    private val context: Context,
    private val photoUris: List<Uri>,
    private val selection: TriageSelection,
    private val loadImage: (ImageView, Uri) -> Unit = { imageView, uri ->
        imageView.load(uri) {
            size(THUMBNAIL_SIZE_PX, THUMBNAIL_SIZE_PX)
            precision(Precision.INEXACT)
        }
    },
) : BaseAdapter() {

    companion object {
        private const val THUMBNAIL_SIZE_PX = 300
    }

    override fun getCount() = photoUris.size

    override fun getItem(position: Int): Uri = photoUris[position]

    override fun getItemId(position: Int) = position.toLong()

    override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
        val view = convertView ?: LayoutInflater.from(context)
            .inflate(R.layout.grid_item_photo_selectable, parent, false)

        val uri = photoUris[position]
        loadImage(view.findViewById(R.id.photo_image), uri)

        view.findViewById<CheckBox>(R.id.selection_checkbox).apply {
            visibility = if (selection.isActive) View.VISIBLE else View.GONE
            isChecked = selection.selected.contains(uri)
        }

        return view
    }
}
