package com.strafeup.fetchservice.model.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.List;

@Data
@AllArgsConstructor
public class ResponseListResultDTO {
    private List<ReadingDTO> result;
}
