package com.strafeup.fetchservice.util;

public class Utils {

    public static String capitalizeWord(String lowercaseWord) {
        return lowercaseWord.substring(0, 1).toUpperCase() + lowercaseWord.substring(1);
    }
}
