namespace TpFileM.Core;

public enum HashPhase
{
    Reading,
    Done,
}

public sealed record HashProgress(HashPhase Phase, double Percent, string StatusKey);
