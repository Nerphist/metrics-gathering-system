package com.strafeup.fetchservice.model.files;

import com.strafeup.fetchservice.command.ExportCommand;
import com.strafeup.fetchservice.model.dto.ReadingDTO;
import lombok.SneakyThrows;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.core.io.InputStreamResource;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.util.List;

public class ReadingListToExcelExporter implements ExportCommand {

    private Workbook workbook;

    private CellStyle headerStyle;
    private CellStyle cellStyle;

    public ReadingListToExcelExporter() {
        this.workbook = createWorkbook();
        setupStyles();
        setupHeader(workbook.getSheet("Metrics"));
    }

    @Override
    @SneakyThrows
    public ResponseEntity<?> execute(List<ReadingDTO> readingDTOList, String fileName) {
        Sheet sheet = workbook.getSheet("Metrics");

        for (int i = 0; i < readingDTOList.size(); i++) {
            Row row = sheet.createRow(i);
            Cell cell = row.createCell(0);
            cell.setCellValue(readingDTOList.get(i).getType());
            cell.setCellStyle(cellStyle);

            cell = row.createCell(1);
            cell.setCellValue(readingDTOList.get(i).getDate().toString());
            cell.setCellStyle(cellStyle);

            cell = row.createCell(2);
            cell.setCellValue(readingDTOList.get(i).getDeviceId());
            cell.setCellStyle(cellStyle);

            cell = row.createCell(3);
            cell.setCellValue(readingDTOList.get(i).getValue());
            cell.setCellStyle(cellStyle);
        }

        FileOutputStream outputStream = new FileOutputStream(fileName + ".xlsx");
        workbook.write(outputStream);
        workbook.close();

        InputStreamResource resourceExcel = new InputStreamResource(new FileInputStream(fileName + ".xlsx"));
        return ResponseEntity.ok()
                .header("Content-Disposition", "attachment; filename=\"" + fileName + ".xlsx\"")
                .contentType(MediaType.APPLICATION_OCTET_STREAM)
                .body(resourceExcel);
    }

    private Sheet returnSheet(int pageNum) {
        Workbook workbook = createWorkbook();
        return workbook.getSheetAt(pageNum);
    }

    private Workbook createWorkbook() {
        Workbook workbook = new XSSFWorkbook();
        workbook.createSheet("Metrics");
        return workbook;
    }

    private void setupHeader(Sheet sheet) {
        Row header = sheet.createRow(0);

        Cell headerCell = header.createCell(0);
        headerCell.setCellValue("Type");
        headerCell.setCellStyle(headerStyle);

        headerCell = header.createCell(1);
        headerCell.setCellValue("Date");
        headerCell.setCellStyle(headerStyle);

        headerCell = header.createCell(1);
        headerCell.setCellValue("Device id");
        headerCell.setCellStyle(headerStyle);

        headerCell = header.createCell(1);
        headerCell.setCellValue("Value");
        headerCell.setCellStyle(headerStyle);
    }

    private void setupStyles() {
        CellStyle _headerStyle = workbook.createCellStyle();
        _headerStyle.setFillForegroundColor(IndexedColors.LIGHT_BLUE.getIndex());
        _headerStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);
        this.headerStyle = _headerStyle;

        CellStyle _cellStyle = workbook.createCellStyle();
        _cellStyle.setWrapText(true);
        this.cellStyle = _cellStyle;
    }
}
