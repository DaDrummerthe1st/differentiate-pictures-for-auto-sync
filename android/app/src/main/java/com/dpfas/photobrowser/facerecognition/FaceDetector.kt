package com.dpfas.photobrowser.facerecognition

import android.graphics.Bitmap

/** Finds faces in a photo. */
interface FaceDetector {
    fun detect(bitmap: Bitmap): List<FaceBox>
}
