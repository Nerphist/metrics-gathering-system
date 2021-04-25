package com.strafeup.fetchservice.model.dto;

import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
public class ReadingDTO {

    public static final ReadingDTO EMPTY_DTO = new ReadingDTO();

    private LocalDateTime date;
    private Double value;
    private String type;

    private int deviceId;

    public ReadingDTO(Double value) {
        this.value = value;
    }
}
