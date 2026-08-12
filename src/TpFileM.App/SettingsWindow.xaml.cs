using System.Windows;
using Microsoft.Win32;
using TpFileM.App.Services;

namespace TpFileM.App;

public partial class SettingsWindow : Window
{
    private readonly AppSettings _settings;
    private readonly Func<LocalizationService> _locFactory;
    private readonly Action _onLanguageChanged;

    public SettingsWindow(AppSettings settings, Func<LocalizationService> locFactory, Action onLanguageChanged)
    {
        InitializeComponent();
        _settings = settings;
        _locFactory = locFactory;
        _onLanguageChanged = onLanguageChanged;
        ApplyLocalization();
        LoadValues();
    }

    private LocalizationService Loc => _locFactory();

    private void LoadValues()
    {
        LanguageCombo.Items.Clear();
        LanguageCombo.Items.Add(new LanguageItem("en", Loc.Get("Lang_en")));
        LanguageCombo.Items.Add(new LanguageItem("zh-TW", Loc.Get("Lang_zh-TW")));
        LanguageCombo.SelectedItem = LanguageCombo.Items
            .Cast<LanguageItem>()
            .FirstOrDefault(i => i.Code == _settings.Language) ?? LanguageCombo.Items[0];

        McpExeBox.Text = _settings.ResolveMcpExePath();
        RefreshMcpJson();

        // Font initialization
        if (_settings.UseSystemFont)
        {
            FontCombo.SelectedIndex = 1;
        }
        else if (!string.IsNullOrWhiteSpace(_settings.CustomFontPath))
        {
            FontCombo.SelectedIndex = 2;
        }
        else
        {
            FontCombo.SelectedIndex = 0;
        }
    }

    private void FontCombo_OnSelectionChanged(object sender, System.Windows.Controls.SelectionChangedEventArgs e)
    {
        if (FontBrowseButton == null) return;

        FontBrowseButton.Visibility = FontCombo.SelectedIndex == 2 ? Visibility.Visible : Visibility.Collapsed;

        if (FontCombo.SelectedIndex == 0) // Monocraft
        {
            _settings.UseSystemFont = false;
            _settings.CustomFontPath = null;
        }
        else if (FontCombo.SelectedIndex == 1) // System
        {
            _settings.UseSystemFont = true;
            _settings.CustomFontPath = null;
        }
        
        _settings.Save();
        ((App)Application.Current).ApplyFontSettings();
    }

    private void FontBrowse_Click(object sender, RoutedEventArgs e)
    {
        var dialog = new OpenFileDialog
        {
            Filter = "Font Files (*.ttf;*.ttc;*.otf)|*.ttf;*.ttc;*.otf|All files (*.*)|*.*",
            Title = "Select Custom Font",
        };

        if (dialog.ShowDialog() == true)
        {
            _settings.UseSystemFont = false;
            _settings.CustomFontPath = dialog.FileName;
            _settings.Save();
            ((App)Application.Current).ApplyFontSettings();
        }
    }

    private void RefreshMcpJson()
    {
        var path = string.IsNullOrWhiteSpace(McpExeBox.Text) ? _settings.ResolveMcpExePath() : McpExeBox.Text;
        McpJsonBox.Text = string.IsNullOrWhiteSpace(path)
            ? "{}"
            : McpSettingsService.BuildMcpJsonSnippet(path);
    }

    private void ApplyLocalization()
    {
        Title = Loc.Get("Settings_Title");
        LanguageLabel.Text = Loc.Get("Settings_Language");
        McpExeLabel.Text = Loc.Get("Settings_McpExe");
        McpJsonLabel.Text = Loc.Get("Settings_McpJson");
        McpBrowseButton.Content = Loc.Get("Settings_McpBrowse");
        CopyMcpJsonButton.Content = Loc.Get("Button_CopyMcpJson");
        TestMcpButton.Content = Loc.Get("Button_TestMcp");
        CloseButton.Content = Loc.Get("Button_Close");
    }

    private void LanguageCombo_OnSelectionChanged(object sender, System.Windows.Controls.SelectionChangedEventArgs e)
    {
        if (LanguageCombo.SelectedItem is not LanguageItem item)
        {
            return;
        }

        if (_settings.Language == item.Code)
        {
            return;
        }

        _settings.Language = item.Code;
        _settings.Save();
        _onLanguageChanged();
        ApplyLocalization();
        LanguageCombo.Items.Clear();
        LanguageCombo.Items.Add(new LanguageItem("en", Loc.Get("Lang_en")));
        LanguageCombo.Items.Add(new LanguageItem("zh-TW", Loc.Get("Lang_zh-TW")));
        LanguageCombo.SelectedItem = LanguageCombo.Items.Cast<LanguageItem>().First(i => i.Code == item.Code);
    }

    private void McpBrowse_Click(object sender, RoutedEventArgs e)
    {
        var dialog = new OpenFileDialog
        {
            Filter = "Executable (*.exe)|*.exe|All files (*.*)|*.*",
            Title = Loc.Get("Settings_McpExe"),
        };

        if (dialog.ShowDialog() == true)
        {
            _settings.McpExePath = dialog.FileName;
            _settings.Save();
            McpExeBox.Text = dialog.FileName;
            RefreshMcpJson();
        }
    }

    private void CopyMcpJson_Click(object sender, RoutedEventArgs e)
    {
        if (!string.IsNullOrWhiteSpace(McpJsonBox.Text))
        {
            Clipboard.SetText(McpJsonBox.Text);
        }
    }

    private async void TestMcp_Click(object sender, RoutedEventArgs e)
    {
        TestMcpButton.IsEnabled = false;
        SettingsStatusText.Text = Loc.Get("Status_Counting");
        try
        {
            var path = McpExeBox.Text;
            var (ok, message) = await McpSettingsService.SmokeTestAsync(path);
            SettingsStatusText.Text = ok
                ? Loc.Get("Settings_McpTestOk")
                : Loc.Format("Settings_McpTestFail", message);
        }
        finally
        {
            TestMcpButton.IsEnabled = true;
        }
    }

    private void CloseButton_Click(object sender, RoutedEventArgs e) => Close();

    private sealed record LanguageItem(string Code, string Label)
    {
        public override string ToString() => Label;
    }
}
