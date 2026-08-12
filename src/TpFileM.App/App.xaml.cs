using System.Windows;
using System.Windows.Media;

namespace TpFileM.App;

public partial class App : Application
{
    protected override void OnStartup(StartupEventArgs e)
    {
        if (!TryLoadMonocraft())
        {
            Resources["PixelFont"] = new FontFamily("Courier New");
        }

        base.OnStartup(e);
    }

    private bool TryLoadMonocraft()
    {
        try
        {
            _ = new FontFamily("pack://application:,,,/Assets/Fonts/#Monocraft");
            return true;
        }
        catch
        {
            return false;
        }
    }
}
