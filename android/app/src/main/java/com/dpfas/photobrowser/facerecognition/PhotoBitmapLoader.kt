package com.dpfas.photobrowser.facerecognition

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
import android.net.Uri
import androidx.exifinterface.media.ExifInterface
import java.io.FileNotFoundException
import java.io.InputStream

/**
 * Decodes a MediaStore photo Uri into a downsampled, EXIF-rotated [Bitmap] suitable for feeding
 * to the face-recognition pipeline. Framework-heavy (real ContentResolver streams, real Bitmap
 * decode/rotate) - exercised via the on-device manual verification path, not unit tests, same as
 * this project's existing stance on not exercising Coil's real decode engine in Robolectric.
 */
object PhotoBitmapLoader {

    private const val MAX_DIMENSION = 1024

    /** Returns null if the photo can no longer be opened (e.g. deleted between the MediaStore query and this scan) or can't be decoded as an image. */
    fun load(context: Context, uri: Uri): Bitmap? {
        val resolver = context.contentResolver

        // decodeStream always returns null in bounds-only mode (inJustDecodeBounds=true) - that's
        // not a decode failure, so success/failure has to be read from bounds.outWidth/outHeight
        // below, not from this call's return value (see documentation/bugs/claude-bugs' matching
        // 2026-09-06 photo-grid bug for the same elvis-operator shape).
        val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        val boundsStream = openInputStreamOrNull(resolver, uri) ?: return null
        boundsStream.use { BitmapFactory.decodeStream(it, null, bounds) }
        if (bounds.outWidth <= 0 || bounds.outHeight <= 0) return null

        var sampleSize = 1
        while (bounds.outWidth / (sampleSize * 2) >= MAX_DIMENSION ||
            bounds.outHeight / (sampleSize * 2) >= MAX_DIMENSION
        ) {
            sampleSize *= 2
        }
        val decodeOptions = BitmapFactory.Options().apply { inSampleSize = sampleSize }
        val decoded = openInputStreamOrNull(resolver, uri)
            ?.use { BitmapFactory.decodeStream(it, null, decodeOptions) }
            ?: return null

        val rotationDegrees = openInputStreamOrNull(resolver, uri)?.use(::readExifRotationDegrees) ?: 0
        return if (rotationDegrees == 0) decoded else rotate(decoded, rotationDegrees)
    }

    /** `ContentResolver.openInputStream` is documented to throw rather than return null when the Uri can't be opened - normalize both to null. */
    private fun openInputStreamOrNull(resolver: android.content.ContentResolver, uri: Uri): InputStream? =
        try {
            resolver.openInputStream(uri)
        } catch (e: FileNotFoundException) {
            null
        }

    private fun readExifRotationDegrees(stream: InputStream): Int =
        when (ExifInterface(stream).getAttributeInt(ExifInterface.TAG_ORIENTATION, ExifInterface.ORIENTATION_NORMAL)) {
            ExifInterface.ORIENTATION_ROTATE_90 -> 90
            ExifInterface.ORIENTATION_ROTATE_180 -> 180
            ExifInterface.ORIENTATION_ROTATE_270 -> 270
            else -> 0
        }

    private fun rotate(bitmap: Bitmap, degrees: Int): Bitmap {
        val matrix = Matrix().apply { postRotate(degrees.toFloat()) }
        return Bitmap.createBitmap(bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true)
    }
}
