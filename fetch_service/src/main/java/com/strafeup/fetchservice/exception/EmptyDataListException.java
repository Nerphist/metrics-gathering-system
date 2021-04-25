package com.strafeup.fetchservice.exception;

public class EmptyDataListException extends RuntimeException {

    public EmptyDataListException() {
    }

    public EmptyDataListException(String message) {
        super(message);
    }

    public EmptyDataListException(String message, Throwable cause) {
        super(message, cause);
    }
}
