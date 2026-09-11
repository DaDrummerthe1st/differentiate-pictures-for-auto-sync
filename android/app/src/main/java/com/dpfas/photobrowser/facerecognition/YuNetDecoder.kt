package com.dpfas.photobrowser.facerecognition

import kotlin.math.exp
import kotlin.math.max
import kotlin.math.min
import kotlin.math.sqrt

/**
 * Decodes YuNet's raw per-stride output tensors (cls/obj/bbox/kps) into [FaceBox]es, and
 * suppresses overlapping detections. Ported directly from OpenCV's own C++ implementation
 * (`modules/objdetect/src/face_detect.cpp`'s `FaceDetectorYNImpl::postProcess`, the ground truth
 * for this exact model's `cls_*`/`obj_*`/`bbox_*`/`kps_*` output layout — the raw ONNX graph has
 * no equivalent of OpenCV's convenience `FaceDetectorYN` wrapper, so this logic has to be
 * reimplemented rather than reused).
 */
object YuNetDecoder {

    val STRIDES = intArrayOf(8, 16, 32)

    /**
     * Decodes one feature-pyramid level. [cls]/[obj] are one score per grid cell (row-major,
     * size cols*rows); [bbox] is 4 values per cell; [kps] is 10 values per cell (5 landmarks x/y).
     */
    fun decodeLevel(
        stride: Int,
        cols: Int,
        rows: Int,
        cls: FloatArray,
        obj: FloatArray,
        bbox: FloatArray,
        kps: FloatArray,
        scoreThreshold: Float,
    ): List<FaceBox> {
        val boxes = mutableListOf<FaceBox>()
        for (r in 0 until rows) {
            for (c in 0 until cols) {
                val idx = r * cols + c

                val clsScore = cls[idx].coerceIn(0f, 1f)
                val objScore = obj[idx].coerceIn(0f, 1f)
                val score = sqrt(clsScore * objScore)
                if (score < scoreThreshold) continue

                val cx = (c + bbox[idx * 4 + 0]) * stride
                val cy = (r + bbox[idx * 4 + 1]) * stride
                val w = exp(bbox[idx * 4 + 2]) * stride
                val h = exp(bbox[idx * 4 + 3]) * stride
                val x1 = cx - w / 2f
                val y1 = cy - h / 2f

                val landmarks = (0 until 5).map { n ->
                    val lx = (kps[idx * 10 + 2 * n] + c) * stride
                    val ly = (kps[idx * 10 + 2 * n + 1] + r) * stride
                    Landmark(lx, ly)
                }

                boxes.add(FaceBox(x1, y1, w, h, score, landmarks))
            }
        }
        return boxes
    }

    /** Greedy IoU-based non-max suppression, highest score first. */
    fun nms(boxes: List<FaceBox>, iouThreshold: Float, topK: Int): List<FaceBox> {
        val remaining = boxes.sortedByDescending { it.score }.toMutableList()
        val kept = mutableListOf<FaceBox>()
        while (remaining.isNotEmpty() && kept.size < topK) {
            val best = remaining.removeAt(0)
            kept.add(best)
            remaining.removeAll { iou(best, it) > iouThreshold }
        }
        return kept
    }

    private fun iou(a: FaceBox, b: FaceBox): Float {
        val interLeft = max(a.left, b.left)
        val interTop = max(a.top, b.top)
        val interRight = min(a.left + a.width, b.left + b.width)
        val interBottom = min(a.top + a.height, b.top + b.height)

        val interW = max(0f, interRight - interLeft)
        val interH = max(0f, interBottom - interTop)
        val interArea = interW * interH

        val unionArea = a.width * a.height + b.width * b.height - interArea
        return if (unionArea <= 0f) 0f else interArea / unionArea
    }
}
