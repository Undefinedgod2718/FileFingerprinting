namespace TpFileM.Core;

public enum FilenameValidationResult
{
    Ok,
    Empty,
    NotFound,
    NotReadable,
}

public static class FilenameValidator
{
    public static FilenameValidationResult ValidatePath(string? path)
    {
        if (string.IsNullOrWhiteSpace(path))
        {
            return FilenameValidationResult.Empty;
        }

        if (!File.Exists(path))
        {
            return FilenameValidationResult.NotFound;
        }

        try
        {
            using var stream = File.Open(path, FileMode.Open, FileAccess.Read, FileShare.Read);
            if (!stream.CanRead)
            {
                return FilenameValidationResult.NotReadable;
            }
        }
        catch (IOException)
        {
            return FilenameValidationResult.NotReadable;
        }
        catch (UnauthorizedAccessException)
        {
            return FilenameValidationResult.NotReadable;
        }

        return FilenameValidationResult.Ok;
    }
}

public static class FilenameValidationMessages
{
    public static string ToMessageKey(FilenameValidationResult result) => result switch
    {
        FilenameValidationResult.Ok => string.Empty,
        FilenameValidationResult.Empty => "Error_Empty",
        FilenameValidationResult.NotFound => "Error_FileNotFound",
        FilenameValidationResult.NotReadable => "Error_FileNotReadable",
        _ => "Error_FileNotFound",
    };

    public static string ToEnglish(FilenameValidationResult result) => result switch
    {
        FilenameValidationResult.Ok => string.Empty,
        FilenameValidationResult.Empty => "Step #1: Please select a file or drag and drop.",
        FilenameValidationResult.NotFound => "Step #1: File name Error! Please select a correct file or drag and drop!",
        FilenameValidationResult.NotReadable => "Step #1: File name Error in SHA! Please select a correct file or drag and drop!",
        _ => "Step #1: File name Error! Please select a correct file or drag and drop!",
    };
}
