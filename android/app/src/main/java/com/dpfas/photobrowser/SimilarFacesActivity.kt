package com.dpfas.photobrowser

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.GridView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.dpfas.photobrowser.facerecognition.FaceMatch
import com.dpfas.photobrowser.facerecognition.FaceScanCache
import com.dpfas.photobrowser.facerecognition.FaceSimilarity
import com.dpfas.photobrowser.facerecognition.NormalizedFaceBox
import com.dpfas.photobrowser.facerecognition.ScannedFace

/**
 * Opened by tapping a detected face in the fullscreen viewer - a grid of cropped face thumbnails
 * from every other scanned photo, ranked by embedding similarity to the tapped face (see
 * documentation/curation/IDENTITY_MATCHING.md's already-designed nearest-neighbor mechanism).
 * No naming/identity UI yet - purely a "find more like this" browse, see documentation/mobile/TODO.md.
 */
class SimilarFacesActivity : AppCompatActivity() {

    companion object {
        const val EXTRA_QUERY_EMBEDDING = "query_embedding"
        const val EXTRA_QUERY_BOX = "query_box"
        private const val TOP_K = 60
        private const val TAG = "FaceScan"

        fun createIntent(context: Context, face: ScannedFace): Intent =
            Intent(context, SimilarFacesActivity::class.java)
                .putExtra(EXTRA_QUERY_EMBEDDING, face.embedding)
                .putExtra(EXTRA_QUERY_BOX, floatArrayOf(face.box.left, face.box.top, face.box.right, face.box.bottom))
    }

    /**
     * [ScannedFace] passed in, not just the embedding, so the tapped face can be excluded from its
     * own results by value - it only ever arrives here reconstructed from Intent extras, never the
     * same instance [FaceScanCache] holds, so reference-based exclusion can't work across this
     * Activity boundary.
     */
    var findMatches: (ScannedFace) -> List<FaceMatch> = { face ->
        FaceSimilarity.findSimilar(face.embedding, FaceScanCache.snapshot(), excludeSelf = face, topK = TOP_K)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_similar_faces)

        val queryEmbedding = intent.getFloatArrayExtra(EXTRA_QUERY_EMBEDDING) ?: return
        val box = intent.getFloatArrayExtra(EXTRA_QUERY_BOX) ?: return
        val queryFace = ScannedFace(NormalizedFaceBox(box[0], box[1], box[2], box[3]), queryEmbedding)
        showMatches(findMatches(queryFace))
    }

    private fun showMatches(matches: List<FaceMatch>) {
        matches.forEachIndexed { rank, match ->
            Log.d(TAG, "similar-faces rank $rank: similarity=${match.similarity} uri=${match.uri}")
        }

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
