package ru.diplom.dbunit;

import org.dbunit.Assertion;
import org.dbunit.database.DatabaseConnection;
import org.dbunit.database.IDatabaseConnection;
import org.dbunit.dataset.IDataSet;
import org.dbunit.dataset.ITable;
import org.dbunit.dataset.SortedTable;
import org.dbunit.dataset.xml.FlatXmlDataSetBuilder;
import org.junit.Test;

import java.io.File;
import java.sql.Connection;
import java.sql.DriverManager;

public class ReadersDbUnitTest {

    private static final String JDBC_URL = "jdbc:mysql://127.0.0.1:3307/center_db"
            + "?useUnicode=true"
            + "&characterEncoding=utf8"
            + "&serverTimezone=UTC"
            + "&allowPublicKeyRetrieval=true"
            + "&useSSL=false";

    private static final String JDBC_USER = "diplom";
    private static final String JDBC_PASSWORD = "diplom";

    @Test
    public void centerReadersTableShouldMatchExpectedDataset() throws Exception {
        Class.forName("com.mysql.cj.jdbc.Driver");

        try (Connection jdbcConnection = DriverManager.getConnection(JDBC_URL, JDBC_USER, JDBC_PASSWORD)) {
            IDatabaseConnection dbUnitConnection = new DatabaseConnection(jdbcConnection, "center_db");

            ITable actualTable = dbUnitConnection.createQueryTable(
                    "readers",
                    "SELECT "
                            + "CAST(reader_id AS CHAR) AS reader_id, "
                            + "full_name, "
                            + "DATE_FORMAT(birth_date, '%Y-%m-%d') AS birth_date, "
                            + "phone, "
                            + "email, "
                            + "CAST(branch_id AS CHAR) AS branch_id, "
                            + "CAST(is_deleted AS CHAR) AS is_deleted "
                            + "FROM readers "
                            + "ORDER BY reader_id"
            );

            File expectedFile = new File("../datasets/expected_center.xml");
            IDataSet expectedDataSet = new FlatXmlDataSetBuilder()
                    .setColumnSensing(true)
                    .build(expectedFile);
            ITable expectedTable = expectedDataSet.getTable("readers");

            SortedTable sortedActual = new SortedTable(actualTable, new String[]{"reader_id"});
            SortedTable sortedExpected = new SortedTable(expectedTable, new String[]{"reader_id"});
            sortedActual.setUseComparable(true);
            sortedExpected.setUseComparable(true);

            Assertion.assertEquals(sortedExpected, sortedActual);
        }
    }
}
