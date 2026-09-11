package com.dpfas.photobrowser

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.GridView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.dpfas.photobrowser.facerecognition.FaceMatch
import com.dpfas.photobrowser.facerecognition.FaceScanCache
import com.dpfas.photobrowser.facerecognition.FaceSimilarity

/**
 * Opened by tapping a detected face in the fullscreen viewer - a grid of cropped face thumbnails
 * from every other scanned photo, ranked by embedding similarity to the tapped face (see
 * documentation/curation/IDENTITY_MATCHING.md's already-designed nearest-neighbor mechanism).
 * No naming/identity UI yet - purely a "find more like this" browse, see documentation/mobile/TODO.md.
 */
class SimilarFacesActivity : AppCompatActivity() {

    companion object {
        const val EXTRA_QUERY_EMBEDDING = "query_embedding"
        private const val TOP_K = 60

        fun createIntent(context: Context, queryEmbedding: FloatArray): Intent =
            Intent(context, SimilarFacesActivity::class.java)
                .putExtra(EXTRA_QUERY_EMBEDDING, queryEmbedding)
    }

    var findMatches: (FloatArray) -> List<FaceMatch> = { query ->
        FaceSimilarity.findSimilar(query, FaceScanCache.snapshot(), topK = TOP_K)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_similar_faces)

        val queryEmbedding = intent.getFloatArrayExtra(EXTRA_QUERY_EMBEDDING) ?: return
        showMatches(findMatches(queryEmbedding))
    }

    private fun showMatches(matches: List<FaceMatch>) {
        val statusText = findViewById<TextView>(R.id.similar_faces_status_text)
        val grid = findViewById<GridView>(R.id.similar_faces_grid)

        if (matches.isEmpty()) {
            statusText.visibility = View.VISIBLE
            grid.visibility = View.GONE
            return
        }

        statusText.visibility = View.GONE
        grid.visibility = View.VISIBLE
        grid.adapter = SimilarFacesAdapter(this, matches)
        grid.setOnItemClickListener { _, _, position, _ ->
            startActivity(FullscreenPhotoActivity.createIntent(this, listOf(matches[position].uri), 0))
        }
    }
}
