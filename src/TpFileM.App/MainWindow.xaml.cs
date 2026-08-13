using System.Globalization;
using System.IO;
using System.Windows;
using System.Windows.Automation;
using System.Windows.Input;
using Microsoft.Win32;
using TpFileM.App.Services;
using TpFileM.Core;

namespace TpFileM.App;

public partial class MainWindow : Window
{
    private readonly AppSettings _settings;
    private LocalizationService _loc;
    private string? _selectedPath;
    private CancellationTokenSource? _generateCts;

    public MainWindow()
    {
        _settings = AppSettings.Load();
        _loc = new LocalizationService(_settings);
        ApplyCulture();
        InitializeComponent();
        ApplyLocalization();
        SetupKeyMode();
    }

    private void ApplyCulture()
    {
        var culture = _loc.Language == "zh-TW"
            ? new CultureInfo("zh-TW")
            : CultureInfo.GetCultureInfo("en");
        CultureInfo.CurrentUICulture = culture;
        CultureInfo.DefaultThreadCurrentUICulture = culture;
    }

    private void ReloadLocalization()
    {
        _loc = new LocalizationService(_settings);
        ApplyCulture();
        ApplyLocalization();
        SetupKeyMode();
    }

    private void SetupKeyMode()
    {
        KeyModeCombo.Items.Clear();
        KeyModeCombo.Items.Add(_loc.Get("KeyMode_Legacy"));
        KeyModeCombo.Items.Add(_loc.Get("KeyMode_Modern"));
        KeyModeCombo.SelectedIndex = 0;
        KeyModeCombo.IsEnabled = false;
    }

    private void ApplyLocalization()
    {
        Title = _loc.Get("Window_Title");
        TitleText.Text = _loc.Get("Window_Title");
        TitleShadowText.Text = _loc.Get("Window_Title");
        TitleShadowDeepText.Text = _loc.Get("Window_Title");
        KeyModeLabel.Text = _loc.Get("Label_KeyMode");
        FileNameLabel.Text = _loc.Get("Label_FileName");
        CrcKeyLabel.Text = _loc.Get("Label_CrcKey");
        ShaKeyLabel.Text = _loc.Get("Label_ShaKey");
        AutomationProperties.SetName(FileNameBox, _loc.Get("Label_FileName"));
        AutomationProperties.SetName(CrcKeyBox, _loc.Get("Label_CrcKey"));
        AutomationProperties.SetName(ShaKeyBox, _loc.Get("Label_ShaKey"));
        SelectFileButton.Content = _loc.Get("Button_SelectFile");
        GenerateKeyButton.Content = _loc.Get("Button_GenerateKey");
        SettingsButton.Content = _loc.Get("Button_Settings");
        QuitButton.Content = _loc.Get("Button_Quit");
        CopyCrcButton.Content = _loc.Get("Button_Copy");
        CopyShaButton.Content = _loc.Get("Button_Copy");

        FileNameBox.ToolTip = _loc.Get("Tooltip_FileName");
        CrcKeyBox.ToolTip = _loc.Get("Tooltip_CrcKey");
        ShaKeyBox.ToolTip = _loc.Get("Tooltip_ShaKey");
        KeyModeCombo.ToolTip = _loc.Get("Tooltip_KeyMode");
        HashProgress.ToolTip = _loc.Get("Tooltip_Progress");
        SelectFileButton.ToolTip = _loc.Get("Tooltip_SelectFile");
        GenerateKeyButton.ToolTip = _loc.Get("Tooltip_GenerateKey");
        SettingsButton.ToolTip = _loc.Get("Tooltip_Settings");
        QuitButton.ToolTip = _loc.Get("Tooltip_Quit");
        CopyCrcButton.ToolTip = _loc.Get("Tooltip_CopyCrc");
        CopyShaButton.ToolTip = _loc.Get("Tooltip_CopySha");

        if (string.IsNullOrWhiteSpace(_selectedPath))
        {
            StatusText.Text = _loc.Get("Status_Step1");
        }
    }

    private void Window_OnLoaded(object sender, RoutedEventArgs e)
    {
        if (string.IsNullOrWhiteSpace(_selectedPath))
        {
            StatusText.Text = _loc.Get("Status_Step1");
        }
    }

    private void SelectFile_Click(object sender, RoutedEventArgs e) => BrowseForFile();

    private void BrowseForFile()
    {
        var dialog = new OpenFileDialog
        {
            Filter = "All Files (*.*)|*.*",
            Title = _loc.Get("Button_SelectFile"),
        };

        if (dialog.ShowDialog() == true)
        {
            SetSelectedFile(dialog.FileName);
        }
    }

    private void SetSelectedFile(string path)
    {
        _selectedPath = path;
        FileNameBox.Text = Path.GetFileName(path);
        CrcKeyBox.Clear();
        ShaKeyBox.Clear();
        HashProgress.Value = 0;

        var validation = FilenameValidator.ValidatePath(path);
        StatusText.Text = validation == FilenameValidationResult.Ok
            ? _loc.Get("Status_Step2")
            : _loc.ValidationMessage(validation);
    }

    private async void GenerateKey_Click(object sender, RoutedEventArgs e)
    {
        if (string.IsNullOrWhiteSpace(_selectedPath))
        {
            StatusText.Text = _loc.Get("Status_NoFile");
            return;
        }

        if (KeyModeCombo.SelectedIndex != 0)
        {
            return;
        }

        _generateCts?.Cancel();
        _generateCts = new CancellationTokenSource();
        var token = _generateCts.Token;

        SetGeneratingUi(true);
        HashProgress.Value = 0;
        StatusText.Text = _loc.Get("Status_Counting");

        try
        {
            var path = _selectedPath;
            var progress = new Progress<HashProgress>(p =>
            {
                HashProgress.Value = p.Percent;
                if (p.Phase == HashPhase.Reading)
                {
                    StatusText.Text = _loc.Get("Status_Counting");
                }
            });

            var result = await Task.Run(
                () => KeyGenerator.GenerateFromPath(path!, progress, token),
                token);

            FileNameBox.Text = result.FileName;
            CrcKeyBox.Text = result.CrcKey;
            ShaKeyBox.Text = result.ShaKey;
            HashProgress.Value = 100;
            StatusText.Text = _loc.Get("Status_Done");
        }
        catch (OperationCanceledException)
        {
            StatusText.Text = _loc.Get("Status_Step2");
        }
        catch (KeyGenerationException ex)
        {
            StatusText.Text = _loc.ValidationMessage(ex.Reason);
        }
        catch (Exception ex)
        {
            StatusText.Text = ex.Message;
        }
        finally
        {
            SetGeneratingUi(false);
        }
    }

    private void SetGeneratingUi(bool generating)
    {
        GenerateKeyButton.IsEnabled = !generating;
        SelectFileButton.IsEnabled = !generating;
    }

    private void Settings_Click(object sender, RoutedEventArgs e)
    {
        var window = new SettingsWindow(_settings, () => _loc, ReloadLocalization)
        {
            Owner = this,
        };
        window.ShowDialog();
    }

    private void Quit_Click(object sender, RoutedEventArgs e) => Close();

    private void CopyCrc_Click(object sender, RoutedEventArgs e)
    {
        if (!string.IsNullOrWhiteSpace(CrcKeyBox.Text))
        {
            Clipboard.SetText(CrcKeyBox.Text);
        }
    }

    private void CopySha_Click(object sender, RoutedEventArgs e)
    {
        if (!string.IsNullOrWhiteSpace(ShaKeyBox.Text))
        {
            Clipboard.SetText(ShaKeyBox.Text);
        }
    }

    private void KeyModeCombo_OnSelectionChanged(object sender, System.Windows.Controls.SelectionChangedEventArgs e)
    {
        if (KeyModeCombo.SelectedIndex != 0)
        {
            KeyModeCombo.SelectedIndex = 0;
        }
    }

    private void Window_OnDragOver(object sender, DragEventArgs e)
    {
        e.Effects = e.Data.GetDataPresent(DataFormats.FileDrop) ? DragDropEffects.Copy : DragDropEffects.None;
        e.Handled = true;
    }

    private void Window_OnDrop(object sender, DragEventArgs e)
    {
        if (!e.Data.GetDataPresent(DataFormats.FileDrop))
        {
            return;
        }

        var files = (string[])e.Data.GetData(DataFormats.FileDrop)!;
        if (files.Length > 0)
        {
            SetSelectedFile(files[0]);
        }
    }

    protected override void OnClosed(EventArgs e)
    {
        _generateCts?.Cancel();
        base.OnClosed(e);
    }
}
