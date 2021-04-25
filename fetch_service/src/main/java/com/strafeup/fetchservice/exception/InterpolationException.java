package com.strafeup.fetchservice.exception;

public class InterpolationException extends RuntimeException {

    public InterpolationException() {
    }

    public InterpolationException(String message) {
        super(message);
    }

    public InterpolationException(String message, Throwable cause) {
        super(message, cause);
    }
}
