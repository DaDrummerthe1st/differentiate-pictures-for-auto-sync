package com.dpfas.photobrowser.facerecognition

import android.content.Context

/** Reads a vendored ONNX model out of assets/models/ - see that folder's LICENSES.md. */
internal fun readModelAsset(context: Context, assetFileName: String): ByteArray =
    context.assets.open("models/$assetFileName").use { it.readBytes() }
