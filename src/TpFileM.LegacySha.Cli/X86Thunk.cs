using System.Runtime.InteropServices;

namespace TpFileM.LegacySha.Cli;

internal static class X86Thunk
{
    // cdecl: void CallWithEcx(void* ctx, void* ecxVal, void* fn)
    private static readonly byte[] CallWithEcxBytes =
    [
        0x55,
        0x8B, 0xEC,
        0x8B, 0x4D, 0x0C,
        0xFF, 0x75, 0x08,
        0xFF, 0x55, 0x10,
        0x5D,
        0xC3,
    ];

    [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
    private delegate void CallWithEcxDelegate(IntPtr ctx, IntPtr ecxVal, IntPtr fn);

    private static readonly CallWithEcxDelegate CallWithEcx = Create<CallWithEcxDelegate>(CallWithEcxBytes);

    public static void InvokeFinal(IntPtr ctx, IntPtr ecxVal, IntPtr finalFn) =>
        CallWithEcx(ctx, ecxVal, finalFn);

    private static T Create<T>(byte[] code) where T : Delegate
    {
        IntPtr mem = Marshal.AllocHGlobal(code.Length);
        Marshal.Copy(code, 0, mem, code.Length);
        if (!VirtualProtect(mem, (UIntPtr)code.Length, 0x40, out _))
        {
            throw new InvalidOperationException("VirtualProtect failed.");
        }

        return Marshal.GetDelegateForFunctionPointer<T>(mem);
    }

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool VirtualProtect(IntPtr addr, UIntPtr size, uint newProtect, out uint oldProtect);
}
