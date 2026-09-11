package com.dpfas.photobrowser.facerecognition

import android.graphics.Bitmap

/** Turns a cropped face into a fixed-length embedding vector, comparable across photos via cosine/L2 distance. */
interface FaceEmbedder {
    fun embed(faceCrop: Bitmap): FloatArray
}
