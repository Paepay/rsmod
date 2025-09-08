package org.rsmod.api.db.sqlite

import jakarta.inject.Inject
import java.sql.Connection
import java.sql.DriverManager
import org.rsmod.api.db.DatabaseConfig

public class SqliteConnection @Inject constructor(private val config: DatabaseConfig) {
    public fun connect(): Connection {
        val connection = DriverManager.getConnection(config.url)
        connection.createStatement().use { statement ->
            statement.execute("PRAGMA foreign_keys = ON;")
            statement.execute("PRAGMA journal_mode = WAL;")
            // Helps avoid SQLITE_BUSY by waiting briefly for locks to clear during contention
            statement.execute("PRAGMA busy_timeout = 5000;")
        }
        connection.autoCommit = false
        return connection
    }
}
