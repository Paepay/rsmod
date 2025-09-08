package org.rsmod.content.areas.external.map

import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.Paths
import org.rsmod.api.type.builders.map.npc.MapNpcSpawnBuilder

object ExternalNpcSpawns : MapNpcSpawnBuilder() {
    override fun onPackMapTask() {
        // Read directly from source tree to avoid classpath/jar URL issues during pack task.
        val projectDir = System.getProperty("user.dir")
        val resourcesDir: Path =
            Paths.get(projectDir, "content", "areas", "external", "src", "main", "resources", "map")
        if (!Files.isDirectory(resourcesDir)) return
        Files.list(resourcesDir).use { stream ->
            stream
                .filter { Files.isRegularFile(it) }
                .map { it.fileName.toString() }
                .filter { it.startsWith("n") && it.contains("_") }
                .sorted()
                .forEach { fileName -> resourceFile<ExternalNpcSpawns>("/map/$fileName") }
        }
    }
}
