package com.dpfas.photobrowser

import android.app.Application
import coil3.ImageLoader
import coil3.PlatformContext
import coil3.SingletonImageLoader
import coil3.util.DebugLogger

class PhotoBrowserApplication : Application(), SingletonImageLoader.Factory {
    override fun newImageLoader(context: PlatformContext): ImageLoader =
        ImageLoader.Builder(context)
            .apply { if (BuildConfig.DEBUG) logger(DebugLogger()) }
            .build()
}
