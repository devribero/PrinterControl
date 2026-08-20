# ─────────────────────────────────────────────────────────────────────────────
#  ARQUIVOS EMBUTIDOS (JSON, XAML E BASE64)
# ─────────────────────────────────────────────────────────────────────────────
$script:configJson = @'
{
    "ServidorPrint": "elgjunprt",
    "TempoRefreshMinutos": 5,
    "FaixaRedeLocal": "10.",
    "SnmpCommunity": "public",
    "ModoOffline": false,
    "WebhookUrl": "https://default44e04f6a5fb4469ea6ffb5c4eec59b.05.environment.api.powerplatform.com:443/powerautomate/automations/direct/cu/27/workflows/fa0f0c3284ab400988b82af36e7c8ac6/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=MQb73Vj9ofxLJ78-Z6IWLcWH0m2OzINh4pics9NnI5Q",
    "DriverMap": [
        { "nome": "DEV_Ricoh_Marketing", "arquivo": "Ricoh\\P502\\driver.inf" },
        { "nome": "DEV_Elgin_Expedicao", "arquivo": "Elgin\\TT042\\setup.exe" }
    ]
}
'@

$script:mockJson = @'
[
    {
        "Nome": "DEV_Ricoh_Marketing",
        "IP": "10.0.0.50",
        "Modelo": "Ricoh P502",
        "Status": "Online",
        "Status": "Online",
        "Toners": [{"Cor": "Preto", "Pct": "78%"}]
    },
    {
        "Nome": "DEV_Elgin_Expedicao",
        "IP": "10.0.0.51",
        "Modelo": "Elgin TT042",
        "Status": "Offline",
        "Toners": []
    }
]
'@

$script:dashboardXaml = @'
<Window
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    Title="Elgin Impressoras" Height="720" Width="1270"
    WindowStartupLocation="CenterScreen" Background="#252525">

    <Window.Resources>
        <Style TargetType="ToolTip">
            <Setter Property="Background" Value="#27272A"/>
            <Setter Property="Foreground" Value="#E4E4E7"/>
            <Setter Property="BorderBrush" Value="#3F3F46"/>
            <Setter Property="BorderThickness" Value="1"/>
            <Setter Property="FontSize" Value="12"/>
            <Setter Property="Padding" Value="8,5"/>
        </Style>

        <Style x:Key="SidebarButton" TargetType="Button">
            <Setter Property="Height" Value="40"/>
            <Setter Property="Margin" Value="0,0,0,5"/>
            <Setter Property="Foreground" Value="#9CA3AF"/>
            <Setter Property="Background" Value="Transparent"/>
            <Setter Property="BorderThickness" Value="0"/>
            <Setter Property="HorizontalContentAlignment" Value="Left"/>
            <Setter Property="Padding" Value="20,0,0,0"/>
            <Setter Property="Cursor" Value="Hand"/>
            <Setter Property="Template">
                <Setter.Value>
                    <ControlTemplate TargetType="Button">
                        <Border Background="{TemplateBinding Background}"
                                BorderBrush="#219AF9"
                                BorderThickness="{TemplateBinding Tag}">
                            <ContentPresenter HorizontalAlignment="Left" VerticalAlignment="Center"
                                              Margin="{TemplateBinding Padding}"/>
                        </Border>
                        <ControlTemplate.Triggers>
                            <Trigger Property="IsMouseOver" Value="True">
                                <Setter Property="Background" Value="#303030"/>
                            </Trigger>
                        </ControlTemplate.Triggers>
                    </ControlTemplate>
                </Setter.Value>
            </Setter>
        </Style>

        <Style TargetType="DataGridColumnHeader">
            <Setter Property="Background" Value="#1E1E1E"/>
            <Setter Property="Foreground" Value="#9CA3AF"/>
            <Setter Property="FontWeight" Value="SemiBold"/>
            <Setter Property="FontSize" Value="11"/>
            <Setter Property="Height" Value="40"/>
            <Setter Property="Padding" Value="10,0"/>
            <Setter Property="BorderThickness" Value="0"/>
        </Style>
    </Window.Resources>

    <Grid>
        <Grid.ColumnDefinitions>
            <ColumnDefinition Width="220"/>
            <ColumnDefinition Width="*"/>
        </Grid.ColumnDefinitions>

        <Border Grid.Column="0" Background="#1c1c1e" BorderBrush="#333" BorderThickness="0,0,1,0">
            <Grid>
                <Grid.RowDefinitions>
                    <RowDefinition Height="Auto"/>
                    <RowDefinition Height="*"/>
                    <RowDefinition Height="Auto"/>
                </Grid.RowDefinitions>

                <Image Grid.Row="0" x:Name="LogoElgin" Height="180" Stretch="Uniform" Margin="0,0,0,0"/>

                <StackPanel Grid.Row="1">
                    <TextBlock Text="STATUS" Foreground="#6B7280" FontSize="11" FontWeight="Bold" Margin="20,0,0,15"/>
                    <Button x:Name="BtnFiltroTodos"   Content="Todos"   Style="{StaticResource SidebarButton}" Background="#2A2A2A" Foreground="White" Tag="3,0,0,0"/>
                    <Button x:Name="BtnFiltroOnline"  Content="Online"  Style="{StaticResource SidebarButton}" Tag="0"/>
                    <Button x:Name="BtnFiltroOffline" Content="Offline" Style="{StaticResource SidebarButton}" Tag="0"/>

                    <TextBlock Text="TIPO" Foreground="#6B7280" FontSize="11" FontWeight="Bold" Margin="20,20,0,15"/>
                    <Button x:Name="BtnTipoTodos"     Content="Todos"     Style="{StaticResource SidebarButton}" Background="#2A2A2A" Foreground="White" Tag="3,0,0,0"/>
                    <Button x:Name="BtnTipoA4"        Content="A4"        Style="{StaticResource SidebarButton}" Tag="0"/>
                    <Button x:Name="BtnTipoEtiqueta"  Content="Etiqueta"  Style="{StaticResource SidebarButton}" Tag="0"/>
                    <Button x:Name="BtnTipoPortatil"  Content="Portátil"  Style="{StaticResource SidebarButton}" Tag="0"/>
                </StackPanel>

                <Border Grid.Row="2" BorderBrush="#333" BorderThickness="0,1,0,0" Margin="20,0,20,0" Padding="0,15,0,20">
                    <StackPanel>
                        <Button x:Name="BtnTrocarServidor" Content="↺  Trocar Servidor"
                                Height="32" Background="#2A2A2A" Foreground="#E4E4E7"
                                FontWeight="SemiBold" BorderThickness="0" Margin="0,0,0,15" Cursor="Hand">
                            <Button.Resources>
                                <Style TargetType="Border"><Setter Property="CornerRadius" Value="4"/></Style>
                            </Button.Resources>
                            <Button.Style>
                                <Style TargetType="Button">
                                    <Setter Property="Background" Value="#2A2A2A"/>
                                    <Style.Triggers>
                                        <Trigger Property="IsMouseOver" Value="True">
                                            <Setter Property="Background" Value="#333333"/>
                                        </Trigger>
                                    </Style.Triggers>
                                </Style>
                            </Button.Style>
                        </Button>
                        <TextBlock x:Name="TxtStatusServico" Text="Impressoras Detectadas"
                                   Foreground="#219AF9" FontSize="12" FontWeight="SemiBold" Margin="0,0,0,5"/>
                        <TextBlock Text="Versão 2.0.1" Foreground="#6B7280" FontSize="11"/>
                        <TextBlock x:Name="UltimaAtualizacao" Foreground="#6B7280" FontSize="10" Margin="0,5,0,0"/>
                    </StackPanel>
                </Border>
            </Grid>
        </Border>

        <Grid Grid.Column="1">
            <Grid.RowDefinitions>
                <RowDefinition Height="70"/>
                <RowDefinition Height="140"/>
                <RowDefinition Height="*"/>
            </Grid.RowDefinitions>

            <Border Grid.Row="0" Background="#219AF9">
                <Grid Margin="20,0">
                    <Border Background="#1860B8" CornerRadius="4" Padding="10,4" HorizontalAlignment="Left" VerticalAlignment="Center">
                        <TextBlock x:Name="RelogioTopo" Text="Carregando hora..." Foreground="White" FontSize="13" FontWeight="SemiBold"/>
                    </Border>

                    <StackPanel Orientation="Horizontal" HorizontalAlignment="Right" VerticalAlignment="Center">
                        <Button x:Name="BtnSino" Width="40" Height="40" Background="Transparent"
                                BorderThickness="0" Cursor="Hand" Margin="0,0,10,0" ToolTip="Notificações">
                            <Button.Style>
                                <Style TargetType="Button">
                                    <Setter Property="Background" Value="Transparent"/>
                                    <Style.Triggers>
                                        <Trigger Property="IsMouseOver" Value="True">
                                            <Setter Property="Background" Value="#1860B8"/>
                                        </Trigger>
                                    </Style.Triggers>
                                </Style>
                            </Button.Style>
                            <Viewbox Width="20" Height="20">
                                <Path Data="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                                      Stroke="White" StrokeThickness="2" Fill="Transparent"/>
                            </Viewbox>
                        </Button>

                        <Button x:Name="BtnExportar" Content="Exportar CSV" Width="110" Height="36"
                                Background="#1872b8" Foreground="White" BorderThickness="0"
                                Margin="0,0,10,0" Cursor="Hand" ToolTip="Exportar lista para CSV">
                            <Button.Resources>
                                <Style TargetType="Border"><Setter Property="CornerRadius" Value="6"/></Style>
                            </Button.Resources>
                            <Button.Style>
                                <Style TargetType="Button">
                                    <Setter Property="Background" Value="#1872b8"/>
                                    <Style.Triggers>
                                        <Trigger Property="IsMouseOver" Value="True">
                                            <Setter Property="Background" Value="#1260a0"/>
                                        </Trigger>
                                    </Style.Triggers>
                                </Style>
                            </Button.Style>
                        </Button>

                        <Button x:Name="BtnEscanear" Content="Escanear Rede" Width="120" Height="36"
                                Background="#2c2c2e" Foreground="White" BorderThickness="0"
                                Cursor="Hand" ToolTip="Varrer a rede em busca de impressoras">
                            <Button.Resources>
                                <Style TargetType="Border"><Setter Property="CornerRadius" Value="6"/></Style>
                            </Button.Resources>
                            <Button.Style>
                                <Style TargetType="Button">
                                    <Setter Property="Background" Value="#2c2c2e"/>
                                    <Style.Triggers>
                                        <Trigger Property="IsMouseOver" Value="True">
                                            <Setter Property="Background" Value="#3a3a3c"/>
                                        </Trigger>
                                    </Style.Triggers>
                                </Style>
                            </Button.Style>
                        </Button>
                    </StackPanel>
                </Grid>
            </Border>

            <Grid Grid.Row="1" Margin="15,15,15,5">
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*"/>
                    <ColumnDefinition Width="*"/>
                    <ColumnDefinition Width="*"/>
                </Grid.ColumnDefinitions>

                <Border Grid.Column="0" Margin="5" Background="#2A2A2A" CornerRadius="8">
                    <StackPanel Margin="20" VerticalAlignment="Center">
                        <TextBlock Text="TOTAL" Foreground="#6B7280" FontSize="11" FontWeight="SemiBold"/>
                        <TextBlock x:Name="Total" Foreground="White" FontSize="40" FontWeight="Bold" Margin="0,4,0,0"/>
                    </StackPanel>
                </Border>

                <Border Grid.Column="1" Margin="5" Background="#2A2A2A" CornerRadius="8">
                    <StackPanel Margin="20" VerticalAlignment="Center">
                        <TextBlock Text="ONLINE" Foreground="#6B7280" FontSize="11" FontWeight="SemiBold"/>
                        <TextBlock x:Name="Online" Foreground="#219AF9" FontSize="40" FontWeight="Bold" Margin="0,4,0,0"/>
                    </StackPanel>
                </Border>

                <Border Grid.Column="2" Margin="5" Background="#2A2A2A" CornerRadius="8">
                    <StackPanel Margin="20" VerticalAlignment="Center">
                        <TextBlock Text="OFFLINE" Foreground="#6B7280" FontSize="11" FontWeight="SemiBold"/>
                        <TextBlock x:Name="Offline" Foreground="#F75C5C" FontSize="40" FontWeight="Bold" Margin="0,4,0,0"/>
                    </StackPanel>
                </Border>
            </Grid>

            <Grid Grid.Row="2" Margin="20,10,20,20">
                <Grid.RowDefinitions>
                    <RowDefinition Height="Auto"/>
                    <RowDefinition Height="*"/>
                </Grid.RowDefinitions>

                <Border Grid.Row="0" Background="#1E1E1E" CornerRadius="8" Height="40" Width="300" HorizontalAlignment="Left" Margin="0,0,0,15">
                    <Grid>
                        <Grid.ColumnDefinitions>
                            <ColumnDefinition Width="36"/>
                            <ColumnDefinition Width="*"/>
                        </Grid.ColumnDefinitions>
                        <Viewbox Grid.Column="0" Width="14" Height="14" Margin="10,0,0,0" HorizontalAlignment="Center" VerticalAlignment="Center" IsHitTestVisible="False">
                            <Path Stroke="#6B7280" StrokeThickness="1.8" Fill="Transparent" StrokeLineJoin="Round" StrokeStartLineCap="Round" StrokeEndLineCap="Round" Data="M11 3 A8 8 0 1 0 11 19 A8 8 0 1 0 11 3 Z M21 21 L16.65 16.65"/>
                        </Viewbox>
                        <TextBox x:Name="TxtPesquisa" Grid.Column="1" Background="Transparent" Foreground="#9CA3AF" BorderThickness="0" Text="Pesquisar impressora..." VerticalAlignment="Center" Padding="0,0,10,0"/>
                    </Grid>
                </Border>

                <DataGrid x:Name="TabelaImpressoras" Grid.Row="1" AutoGenerateColumns="False" Background="#2A2A2A" BorderThickness="0" HeadersVisibility="Column" RowBackground="#2A2A2A" AlternatingRowBackground="#252525" SelectionMode="Single" CanUserResizeRows="False" CanUserAddRows="False" IsReadOnly="True" RowHeight="50" GridLinesVisibility="None">
                    <DataGrid.Resources>
                        <Style TargetType="DataGridCell">
                            <Setter Property="BorderThickness" Value="0"/>
                            <Setter Property="FocusVisualStyle" Value="{x:Null}"/>
                            <Style.Triggers>
                                <Trigger Property="IsSelected" Value="True">
                                    <Setter Property="Background" Value="Transparent"/>
                                    <Setter Property="Foreground" Value="White"/>
                                </Trigger>
                            </Style.Triggers>
                        </Style>
                        <Style TargetType="DataGridRow">
                            <Setter Property="Background" Value="#2A2A2A"/>
                            <Setter Property="BorderThickness" Value="0"/>
                            <Style.Triggers>
                                <Trigger Property="IsMouseOver" Value="True">
                                    <Setter Property="Background" Value="#303030"/>
                                </Trigger>
                                <Trigger Property="IsSelected" Value="True">
                                    <Setter Property="Background" Value="#333333"/>
                                    <Setter Property="BorderBrush" Value="Transparent"/>
                                </Trigger>
                                <DataTrigger Binding="{Binding IsChildRow}" Value="True">
                                    <Setter Property="Background" Value="#232323"/>
                                </DataTrigger>
                            </Style.Triggers>
                        </Style>
                    </DataGrid.Resources>

                    <DataGrid.Columns>
                        <DataGridTemplateColumn Header="NOME" Width="2.5*">
                            <DataGridTemplateColumn.CellTemplate>
                                <DataTemplate>
                                    <StackPanel Orientation="Horizontal" VerticalAlignment="Center">
                                        <Button x:Name="BtnExpandirGrupo" Width="18" Height="18" Margin="0,0,6,0"
                                                Background="Transparent" BorderThickness="0" Cursor="Hand"
                                                Visibility="{Binding ExpansorVis}"
                                                ToolTip="Outras impressoras neste IP">
                                            <Viewbox Width="9" Height="9">
                                                <Path Fill="#9CA3AF">
                                                    <Path.Style>
                                                        <Style TargetType="Path">
                                                            <Setter Property="Data" Value="M2 2 L8 6 L2 10 Z"/>
                                                            <Style.Triggers>
                                                                <DataTrigger Binding="{Binding Expandido}" Value="True">
                                                                    <Setter Property="Data" Value="M2 3 L10 3 L6 9 Z"/>
                                                                </DataTrigger>
                                                            </Style.Triggers>
                                                        </Style>
                                                    </Path.Style>
                                                </Path>
                                            </Viewbox>
                                        </Button>
                                        <TextBlock Text="{Binding Nome}" Foreground="White" VerticalAlignment="Center" Margin="{Binding IndentMargin}"/>
                                        <Border Background="#219AF9" CornerRadius="8" Padding="6,1" Margin="6,0,0,0"
                                                Visibility="{Binding ExpansorVis}" VerticalAlignment="Center">
                                            <TextBlock FontSize="9" FontWeight="Bold" Foreground="White">
                                                <TextBlock.Text>
                                                    <Binding Path="QtdGrupo" StringFormat="+{0}"/>
                                                </TextBlock.Text>
                                            </TextBlock>
                                        </Border>
                                    </StackPanel>
                                </DataTemplate>
                            </DataGridTemplateColumn.CellTemplate>
                        </DataGridTemplateColumn>
                        <DataGridTextColumn Header="ENDEREÇO IP" Binding="{Binding IP}" Width="1*" Foreground="White"/>
                        <DataGridTextColumn Header="MODELO" Binding="{Binding Modelo}" Width="2*" Foreground="#9CA3AF"/>

                        <DataGridTemplateColumn Header="TONER" Width="2*">
                            <DataGridTemplateColumn.CellTemplate>
                                <DataTemplate>
                                    <ItemsControl ItemsSource="{Binding ListaToners}" VerticalAlignment="Center" Margin="10,0">
                                        <ItemsControl.ItemsPanel>
                                            <ItemsPanelTemplate>
                                                <StackPanel Orientation="Horizontal"/>
                                            </ItemsPanelTemplate>
                                        </ItemsControl.ItemsPanel>
                                        <ItemsControl.ItemTemplate>
                                            <DataTemplate>
                                                <StackPanel Margin="0,0,6,0" Visibility="{Binding Vis}">
                                                    <TextBlock Text="{Binding Valor}" FontSize="10" Foreground="{Binding Cor}" HorizontalAlignment="Center" Margin="0,0,0,2"/>
                                                    <Border Height="4" Width="{Binding MaxWidth}" Background="#404040" CornerRadius="2">
                                                        <Border Height="4" Width="{Binding Width}" Background="{Binding Cor}" CornerRadius="2" HorizontalAlignment="Left"/>
                                                    </Border>
                                                </StackPanel>
                                            </DataTemplate>
                                        </ItemsControl.ItemTemplate>
                                    </ItemsControl>
                                </DataTemplate>
                            </DataGridTemplateColumn.CellTemplate>
                        </DataGridTemplateColumn>

                        <DataGridTemplateColumn Header="STATUS" Width="1*">
                            <DataGridTemplateColumn.CellTemplate>
                                <DataTemplate>
                                    <StackPanel Orientation="Horizontal" VerticalAlignment="Center">
                                        <Ellipse Width="8" Height="8" Margin="10,0,6,0">
                                            <Ellipse.Style>
                                                <Style TargetType="Ellipse">
                                                    <Setter Property="Fill" Value="#F75C5C"/>
                                                    <Style.Triggers>
                                                        <DataTrigger Binding="{Binding Status}" Value="Online">
                                                            <Setter Property="Fill" Value="#219AF9"/>
                                                        </DataTrigger>
                                                    </Style.Triggers>
                                                </Style>
                                            </Ellipse.Style>
                                        </Ellipse>
                                        <TextBlock Text="{Binding Status}" FontSize="12" FontWeight="SemiBold" Foreground="White"/>
                                    </StackPanel>
                                </DataTemplate>
                            </DataGridTemplateColumn.CellTemplate>
                        </DataGridTemplateColumn>

                        <DataGridTemplateColumn Header="AÇÕES" Width="160">
                            <DataGridTemplateColumn.CellTemplate>
                                <DataTemplate>
                                    <StackPanel Orientation="Horizontal" VerticalAlignment="Center">
                                        <Button x:Name="BtnAbrirCard" Width="30" Height="30" Background="#333" BorderThickness="0" Margin="0,0,5,0" Cursor="Hand" ToolTip="Detalhes">
                                            <Button.Resources>
                                                <Style TargetType="Border"><Setter Property="CornerRadius" Value="4"/></Style>
                                            </Button.Resources>
                                            <Button.Style>
                                                <Style TargetType="Button">
                                                    <Setter Property="Background" Value="#333"/>
                                                    <Style.Triggers>
                                                        <Trigger Property="IsMouseOver" Value="True">
                                                            <Setter Property="Background" Value="#444"/>
                                                        </Trigger>
                                                    </Style.Triggers>
                                                </Style>
                                            </Button.Style>
                                            <Viewbox Width="14" Height="14">
                                                <Path Stroke="White" StrokeThickness="1.5" Fill="Transparent" StrokeLineJoin="Round" StrokeStartLineCap="Round" StrokeEndLineCap="Round" Data="M14 2H6 C4.9 2 4 2.9 4 4 L4 20 C4 21.1 4.9 22 6 22 L18 22 C19.1 22 20 21.1 20 20 L20 8 Z M14 2 L14 8 L20 8 M8 13 L16 13 M8 17 L16 17"/>
                                            </Viewbox>
                                        </Button>
                                        <Button x:Name="BtnAbrirSite" Width="30" Height="30" Background="#333" BorderThickness="0" Margin="0,0,5,0" Cursor="Hand" ToolTip="Acessar Web">
                                            <Button.Resources>
                                                <Style TargetType="Border"><Setter Property="CornerRadius" Value="4"/></Style>
                                            </Button.Resources>
                                            <Button.Style>
                                                <Style TargetType="Button">
                                                    <Setter Property="Background" Value="#333"/>
                                                    <Style.Triggers>
                                                        <Trigger Property="IsMouseOver" Value="True">
                                                            <Setter Property="Background" Value="#444"/>
                                                        </Trigger>
                                                    </Style.Triggers>
                                                </Style>
                                            </Button.Style>
                                            <Viewbox Width="14" Height="14">
                                                <Path Stroke="White" StrokeThickness="1.5" Fill="Transparent" StrokeLineJoin="Round" StrokeStartLineCap="Round" StrokeEndLineCap="Round" Data="M12 2 A10 10 0 1 0 12 22 A10 10 0 1 0 12 2 Z M2 12 L22 12 M12 2 C9.5 6 8 9 8 12 C8 15 9.5 18 12 22 M12 2 C14.5 6 16 9 16 12 C16 15 14.5 18 12 22"/>
                                            </Viewbox>
                                        </Button>
                                        <Button x:Name="BtnImprimirTeste" Width="30" Height="30" Background="#333" BorderThickness="0" Margin="0,0,5,0" Cursor="Hand" ToolTip="Página de Teste">
                                            <Button.Resources>
                                                <Style TargetType="Border"><Setter Property="CornerRadius" Value="4"/></Style>
                                            </Button.Resources>
                                            <Button.Style>
                                                <Style TargetType="Button">
                                                    <Setter Property="Background" Value="#333"/>
                                                    <Style.Triggers>
                                                        <Trigger Property="IsMouseOver" Value="True">
                                                            <Setter Property="Background" Value="#444"/>
                                                        </Trigger>
                                                    </Style.Triggers>
                                                </Style>
                                            </Button.Style>
                                            <Viewbox Width="14" Height="14">
                                                <Path Stroke="White" StrokeThickness="1.5" Fill="Transparent" StrokeLineJoin="Round" StrokeStartLineCap="Round" StrokeEndLineCap="Round" Data="M7 9 L7 3 L17 3 L17 9 M6 18 L4 18 C2.9 18 2 17.1 2 16 L2 11 C2 9.9 2.9 9 4 9 L20 9 C21.1 9 22 9.9 22 11 L22 16 C22 17.1 21.1 18 20 18 L18 18 M7 14 L17 14 L17 21 L7 21 Z"/>
                                            </Viewbox>
                                        </Button>
                                        <Button x:Name="BtnDriver" Width="30" Height="30" Background="#333" BorderThickness="0" Cursor="Hand" ToolTip="Gerenciar Driver">
                                            <Button.Resources>
                                                <Style TargetType="Border"><Setter Property="CornerRadius" Value="4"/></Style>
                                            </Button.Resources>
                                            <Button.Style>
                                                <Style TargetType="Button">
                                                    <Setter Property="Background" Value="#333"/>
                                                    <Style.Triggers>
                                                        <Trigger Property="IsMouseOver" Value="True">
                                                            <Setter Property="Background" Value="#444"/>
                                                        </Trigger>
                                                    </Style.Triggers>
                                                </Style>
                                            </Button.Style>
                                            <Viewbox Width="14" Height="14">
                                                <Path Stroke="White" StrokeThickness="1.5" Fill="Transparent" StrokeLineJoin="Round" StrokeStartLineCap="Round" StrokeEndLineCap="Round" Data="M12 9 A3 3 0 1 0 12 15 A3 3 0 1 0 12 9 Z M19.4 15 C19.8 15.8 20 16.9 19.4 17.6 L18 19 C17.3 19.7 16.2 19.9 15.4 19.4 L15.4 19.4 C14.6 19 13.8 19.2 13.4 19.9 L13.4 19.9 C13 20.6 12.6 21 12 21 L10 21 C9.4 21 9 20.6 8.6 19.9 L8.6 19.9 C8.2 19.2 7.4 19 6.6 19.4 L6.6 19.4 C5.8 19.9 4.7 19.7 4 19 L2.6 17.6 C1.9 16.9 2.1 15.8 2.6 15 L2.6 15 C3 14.2 2.8 13.4 2.1 13 L2.1 13 C1.4 12.6 1 12.2 1 11.6 L1 9.6 C1 9 1.4 8.4 2.1 8 L2.1 8 C2.8 7.6 3 6.8 2.6 6 L2.6 6 C2.1 5.2 2.3 4.1 3 3.4 L4.4 2 C5.1 1.3 6.2 1.1 7 1.6 L7 1.6 C7.8 2 8.6 1.8 9 1.1 L9 1.1 C9.4 0.4 9.8 0 10.4 0 L12.4 0 C13 0 13.6 0.4 14 1.1 L14 1.1 C14.4 1.8 15.2 2 16 1.6 L16 1.6 C16.8 1.1 17.9 1.3 18.6 2 L20 3.4 C20.7 4.1 20.5 5.2 20 6 L20 6 C19.6 6.8 19.8 7.6 20.5 8 L20.5 8 C21.2 8.4 21.6 8.8 21.6 9.4 L21.6 11.4 C21.6 12 21.2 12.6 20.5 13 L20.5 13 C19.8 13.4 19.6 14.2 20 15 Z"/>
                                            </Viewbox>
                                        </Button>
                                    </StackPanel>
                                </DataTemplate>
                            </DataGridTemplateColumn.CellTemplate>
                        </DataGridTemplateColumn>
                    </DataGrid.Columns>
                </DataGrid>
            </Grid>
        </Grid>
    </Grid>
</Window>
'@

$script:cardDetalhesXaml = @'
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Detalhes do Equipamento" Height="480" Width="470"
        WindowStartupLocation="CenterScreen" WindowStyle="None" AllowsTransparency="True"
        Background="Transparent" ResizeMode="NoResize" ShowInTaskbar="False">

    <Window.Resources>
        <Style TargetType="ToolTip">
            <Setter Property="Background" Value="#27272A"/>
            <Setter Property="Foreground" Value="#E4E4E7"/>
            <Setter Property="BorderBrush" Value="#3F3F46"/>
            <Setter Property="BorderThickness" Value="1"/>
            <Setter Property="FontSize" Value="12"/>
        </Style>
    </Window.Resources>

    <Border Background="#18181B" CornerRadius="14" BorderBrush="#2E2E33" BorderThickness="1" Margin="18">
        <Border.Effect>
            <DropShadowEffect Color="#000000" BlurRadius="28" ShadowDepth="6" Opacity="0.45"/>
        </Border.Effect>

        <Grid Margin="26,24,26,22">
            <Grid.RowDefinitions>
                <RowDefinition Height="Auto"/>
                <RowDefinition Height="Auto"/>
                <RowDefinition Height="*"/>
                <RowDefinition Height="Auto"/>
            </Grid.RowDefinitions>

            <StackPanel x:Name="PnlCabecalho" Grid.Row="0" Margin="0,0,0,20" Cursor="SizeAll">
                <Grid>
                    <Grid.ColumnDefinitions>
                        <ColumnDefinition Width="*"/>
                        <ColumnDefinition Width="Auto"/>
                    </Grid.ColumnDefinitions>
                    <StackPanel Grid.Column="0">
                        <TextBlock x:Name="TxtNome" Foreground="#FFFFFF" FontSize="19" FontWeight="Bold" TextWrapping="Wrap"/>
                        <TextBlock x:Name="TxtModelo" Foreground="#8B8B93" FontSize="13" Margin="0,4,0,0"/>
                    </StackPanel>
                    <Button x:Name="BtnFecharX" Grid.Column="1" Content="✕" Width="28" Height="28" VerticalAlignment="Top"
                            Foreground="#8B8B93" Background="Transparent" BorderThickness="0" FontSize="13" Cursor="Hand">
                        <Button.Style>
                            <Style TargetType="Button">
                                <Setter Property="Template">
                                    <Setter.Value>
                                        <ControlTemplate TargetType="Button">
                                            <Border Background="{TemplateBinding Background}" CornerRadius="14">
                                                <ContentPresenter HorizontalAlignment="Center" VerticalAlignment="Center"/>
                                            </Border>
                                        </ControlTemplate>
                                    </Setter.Value>
                                </Setter>
                                <Style.Triggers>
                                    <Trigger Property="IsMouseOver" Value="True">
                                        <Setter Property="Background" Value="#2A2A2E"/>
                                        <Setter Property="Foreground" Value="#FFFFFF"/>
                                    </Trigger>
                                </Style.Triggers>
                            </Style>
                        </Button.Style>
                    </Button>
                </Grid>
                <Border Height="1" Background="#26262B" Margin="0,18,0,0"/>
            </StackPanel>

            <Border Grid.Row="1" Background="#212124" CornerRadius="10" Padding="16" Margin="0,0,0,15" BorderBrush="#2E2E33" BorderThickness="1">
                <Grid>
                    <Grid.ColumnDefinitions>
                        <ColumnDefinition Width="120"/>
                        <ColumnDefinition Width="*"/>
                    </Grid.ColumnDefinitions>
                    <Grid.RowDefinitions>
                        <RowDefinition Height="Auto"/>
                        <RowDefinition Height="Auto"/>
                        <RowDefinition Height="Auto"/>
                        <RowDefinition Height="Auto"/>
                    </Grid.RowDefinitions>
                    <TextBlock Grid.Row="0" Grid.Column="0" Text="Endereço IP:" Foreground="#8B8B93" Margin="0,6" FontSize="13"/>
                    <TextBlock x:Name="TxtIP" Grid.Row="0" Grid.Column="1" Foreground="White" FontWeight="Bold" Margin="0,6" FontSize="13"/>
                    <TextBlock Grid.Row="1" Grid.Column="0" Text="Status atual:" Foreground="#8B8B93" Margin="0,6" FontSize="13"/>
                    <TextBlock x:Name="TxtStatus" Grid.Row="1" Grid.Column="1" Foreground="#219AF9" FontWeight="Bold" Margin="0,6" FontSize="13"/>
                    <TextBlock Grid.Row="2" Grid.Column="0" Text="Tempo Online:" Foreground="#8B8B93" Margin="0,6" FontSize="13"/>
                    <TextBlock x:Name="TxtUptime" Grid.Row="2" Grid.Column="1" Foreground="White" FontWeight="Bold" Margin="0,6" FontSize="13"/>
                    <TextBlock Grid.Row="3" Grid.Column="0" Text="Págs. Impressas:" Foreground="#8B8B93" Margin="0,6" FontSize="13"/>
                    <TextBlock x:Name="TxtPaginas" Grid.Row="3" Grid.Column="1" Foreground="White" FontWeight="Bold" Margin="0,6" FontSize="13"/>
                </Grid>
            </Border>

            <Border Grid.Row="2" Background="#212124" CornerRadius="10" Padding="16" BorderBrush="#2E2E33" BorderThickness="1">
                <StackPanel>
                    <TextBlock Text="NÍVEIS DE SUPRIMENTOS" Foreground="#8B8B93" FontSize="10.5" FontWeight="Bold" Margin="0,0,0,10"/>
                    <ItemsControl x:Name="TonerContainer">
                        <ItemsControl.ItemTemplate>
                            <DataTemplate>
                                <Grid Margin="0,0,0,12" Visibility="{Binding Vis}">
                                    <Grid.ColumnDefinitions>
                                        <ColumnDefinition Width="55"/>
                                        <ColumnDefinition Width="*"/>
                                    </Grid.ColumnDefinitions>
                                    <TextBlock Grid.Column="0" Text="{Binding Valor}" Foreground="{Binding Cor}" FontSize="12" FontWeight="Bold" VerticalAlignment="Center"/>
                                    <Border Grid.Column="1" Height="10" Background="#33343A" CornerRadius="5" Margin="5,0,0,0">
                                        <Border Height="10" Width="{Binding Width}" MaxWidth="{Binding MaxWidth}" Background="{Binding Cor}" CornerRadius="5" HorizontalAlignment="Left"/>
                                    </Border>
                                </Grid>
                            </DataTemplate>
                        </ItemsControl.ItemTemplate>
                    </ItemsControl>
                </StackPanel>
            </Border>

            <StackPanel Grid.Row="3" Orientation="Horizontal" HorizontalAlignment="Right" Margin="0,20,0,0">
                <Button x:Name="BtnAlertaToner" Content="Enviar Alerta" Width="120" Height="38" Margin="0,0,10,0"
                        Foreground="White" FontWeight="SemiBold" BorderThickness="0" Cursor="Hand">
                    <Button.Resources>
                        <Style TargetType="Border"><Setter Property="CornerRadius" Value="8"/></Style>
                    </Button.Resources>
                    <Button.Style>
                        <Style TargetType="Button">
                            <Setter Property="Background" Value="#219AF9"/>
                            <Style.Triggers>
                                <Trigger Property="IsMouseOver" Value="True">
                                    <Setter Property="Background" Value="#1880d8"/>
                                </Trigger>
                            </Style.Triggers>
                        </Style>
                    </Button.Style>
                </Button>
                <Button x:Name="BtnFecharCard" Content="Fechar" Width="100" Height="38"
                        Foreground="White" FontWeight="SemiBold" BorderThickness="0" Cursor="Hand">
                    <Button.Resources>
                        <Style TargetType="Border"><Setter Property="CornerRadius" Value="8"/></Style>
                    </Button.Resources>
                    <Button.Style>
                        <Style TargetType="Button">
                            <Setter Property="Background" Value="#2E2E33"/>
                            <Style.Triggers>
                                <Trigger Property="IsMouseOver" Value="True">
                                    <Setter Property="Background" Value="#3A3A40"/>
                                </Trigger>
                            </Style.Triggers>
                        </Style>
                    </Button.Style>
                </Button>
            </StackPanel>
        </Grid>
    </Border>
</Window>
'@

$script:driverPopupXaml = @'
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Gerenciador de Driver" Height="410" Width="540"
        WindowStartupLocation="CenterScreen" ShowInTaskbar="False"
        WindowStyle="None" AllowsTransparency="True" Background="Transparent" ResizeMode="NoResize">

    <Window.Resources>
        <Style TargetType="ToolTip">
            <Setter Property="Background" Value="#27272A"/>
            <Setter Property="Foreground" Value="#E4E4E7"/>
            <Setter Property="BorderBrush" Value="#3F3F46"/>
            <Setter Property="BorderThickness" Value="1"/>
            <Setter Property="FontSize" Value="12"/>
        </Style>
    </Window.Resources>

    <Border Background="#18181B" CornerRadius="14" BorderBrush="#2E2E33" BorderThickness="1" Margin="18">
        <Border.Effect>
            <DropShadowEffect Color="#000000" BlurRadius="28" ShadowDepth="6" Opacity="0.45"/>
        </Border.Effect>

        <Grid Margin="26,24,26,22">
            <Grid.RowDefinitions>
                <RowDefinition Height="Auto"/>
                <RowDefinition Height="*"/>
                <RowDefinition Height="Auto"/>
            </Grid.RowDefinitions>

            <StackPanel x:Name="PnlCabecalho" Grid.Row="0" Margin="0,0,0,20" Cursor="SizeAll">
                <Grid>
                    <Grid.ColumnDefinitions>
                        <ColumnDefinition Width="*"/>
                        <ColumnDefinition Width="Auto"/>
                    </Grid.ColumnDefinitions>
                    <StackPanel Grid.Column="0">
                        <TextBlock x:Name="TxtNome" Foreground="#FFFFFF" FontSize="19" FontWeight="Bold" TextWrapping="Wrap"/>
                        <TextBlock x:Name="TxtModelo" Foreground="#8B8B93" FontSize="13" Margin="0,4,0,0"/>
                    </StackPanel>
                    <Button x:Name="BtnFecharX" Grid.Column="1" Content="✕" Width="28" Height="28" VerticalAlignment="Top"
                            Foreground="#8B8B93" Background="Transparent" BorderThickness="0" FontSize="13" Cursor="Hand">
                        <Button.Style>
                            <Style TargetType="Button">
                                <Setter Property="Template">
                                    <Setter.Value>
                                        <ControlTemplate TargetType="Button">
                                            <Border Background="{TemplateBinding Background}" CornerRadius="14">
                                                <ContentPresenter HorizontalAlignment="Center" VerticalAlignment="Center"/>
                                            </Border>
                                        </ControlTemplate>
                                    </Setter.Value>
                                </Setter>
                                <Style.Triggers>
                                    <Trigger Property="IsMouseOver" Value="True">
                                        <Setter Property="Background" Value="#2A2A2E"/>
                                        <Setter Property="Foreground" Value="#FFFFFF"/>
                                    </Trigger>
                                </Style.Triggers>
                            </Style>
                        </Button.Style>
                    </Button>
                </Grid>
                <Border Height="1" Background="#26262B" Margin="0,18,0,0"/>
            </StackPanel>

            <StackPanel Grid.Row="1">
                <Border Background="#212124" CornerRadius="10" Padding="16" Margin="0,0,0,12" BorderBrush="#2E2E33" BorderThickness="1">
                    <StackPanel>
                        <TextBlock Text="STATUS DO DRIVER LOCAL" Foreground="#8B8B93" FontSize="10.5" FontWeight="Bold" Margin="0,0,0,8"/>
                        <TextBlock x:Name="TxtStatusDriver" Foreground="#219AF9" FontSize="14" FontWeight="SemiBold" TextWrapping="Wrap" LineHeight="20"/>
                    </StackPanel>
                </Border>

                <Border Background="#212124" CornerRadius="10" Padding="16" BorderBrush="#2E2E33" BorderThickness="1">
                    <StackPanel>
                        <TextBlock Text="REPOSITÓRIO / INSTRUÇÃO DE INSTALAÇÃO" Foreground="#8B8B93" FontSize="10.5" FontWeight="Bold" Margin="0,0,0,8"/>
                        <ScrollViewer VerticalScrollBarVisibility="Auto" MaxHeight="80">
                            <TextBlock x:Name="TxtInstrucao" Foreground="#D4D4D8" FontSize="12.5" FontFamily="Consolas" TextWrapping="Wrap" LineHeight="18"/>
                        </ScrollViewer>
                    </StackPanel>
                </Border>
            </StackPanel>

            <StackPanel Grid.Row="2" Orientation="Horizontal" HorizontalAlignment="Right" Margin="0,20,0,0">
                <Button x:Name="BtnFechar" Content="Fechar" Width="94" Height="38" Margin="0,0,10,0" Foreground="#FFFFFF" FontWeight="SemiBold" BorderThickness="0" Cursor="Hand">
                    <Button.Resources>
                        <Style TargetType="Border"><Setter Property="CornerRadius" Value="8"/></Style>
                    </Button.Resources>
                    <Button.Style>
                        <Style TargetType="Button">
                            <Setter Property="Background" Value="#2E2E33"/>
                            <Style.Triggers>
                                <Trigger Property="IsMouseOver" Value="True">
                                    <Setter Property="Background" Value="#3A3A40"/>
                                </Trigger>
                            </Style.Triggers>
                        </Style>
                    </Button.Style>
                </Button>
                <Button x:Name="BtnAcao" Content="Instalar Driver" Width="160" Height="38" Foreground="#FFFFFF" FontWeight="Bold" BorderThickness="0" Cursor="Hand">
                    <Button.Resources>
                        <Style TargetType="Border"><Setter Property="CornerRadius" Value="8"/></Style>
                    </Button.Resources>
                    <Button.Style>
                        <Style TargetType="Button">
                            <Setter Property="Background" Value="#219AF9"/>
                            <Style.Triggers>
                                <Trigger Property="IsMouseOver" Value="True">
                                    <Setter Property="Background" Value="#1880d8"/>
                                </Trigger>
                            </Style.Triggers>
                        </Style>
                    </Button.Style>
                </Button>
            </StackPanel>
        </Grid>
    </Border>
</Window>
'@


# ─────────────────────────────────────────────────────────────────────────────
#  INICIALIZAÇÃO DO SISTEMA
# ─────────────────────────────────────────────────────────────────────────────
$script:Config = $script:configJson | ConvertFrom-Json

Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName PresentationCore

# Transcript de diagnóstico
try {
    $script:TranscriptPath = Join-Path $env:TEMP "NOC-Impressoras-Transcript.log"
    Start-Transcript -Path $script:TranscriptPath -Force -ErrorAction Stop | Out-Null
} catch {
}

# Deteccao de elevacao. Nao bloqueia o boot: se nao estiver elevado, PERGUNTA
# uma unica vez (nao forca) se quer relancar a ferramenta inteira como
# Administrador via UAC - mesmo padrao do ServiceDeskTool.ps1 (Request-
# AdminElevation). Se o usuario recusar ou cancelar o UAC, o app continua
# rodando sem admin; cada acao que precisa de admin verifica $script:IsElevated
# e mostra aviso pontual em vez de travar o app inteiro.
$script:IsElevated = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $script:IsElevated -and $PSCommandPath) {
    $quer = [System.Windows.MessageBox]::Show(
        "Para instalar drivers de impressora, esta ferramenta precisa de permissao administrativa.`n`nDeseja reabrir agora como Administrador? (O Windows exibira a janela oficial do UAC.)`n`nSe recusar, a ferramenta continua aberta, mas as acoes que exigem administrador ficarao bloqueadas.",
        "Elevacao opcional", 4, 32
    )
    if ($quer -eq "Yes") {
        try {
            $procElevado = Start-Process -FilePath "powershell.exe" `
                -ArgumentList @("-NoProfile", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $PSCommandPath) `
                -Verb RunAs -WorkingDirectory $PSScriptRoot -ErrorAction Stop -PassThru

            Start-Sleep -Seconds 3
            $procElevado.Refresh()
            if ($procElevado.HasExited) {
                [System.Windows.MessageBox]::Show(
                    "DIAGNOSTICO: o processo elevado (PID $($procElevado.Id)) abriu e ja fechou sozinho em menos de 3 segundos, com codigo de saida $($procElevado.ExitCode).`n`nIsso indica que o processo esta encerrando muito rapido pra dar tempo do -NoExit segurar - pode ser bloqueio de politica de grupo/AV no proprio powershell.exe elevado, nao um erro do script. A ferramenta vai continuar aberta sem admin.",
                    "Diagnostico de elevacao", 0, 48
                ) | Out-Null
            } else {
                [System.Windows.MessageBox]::Show(
                    "DIAGNOSTICO: o processo elevado (PID $($procElevado.Id)) esta rodando normalmente apos 3 segundos.`n`nProcure uma janela de PowerShell na barra de tarefas ou no Alt+Tab - ela pode ter aberto atras desta ou minimizada. Esta janela (sem admin) vai fechar agora.",
                    "Diagnostico de elevacao", 0, 64
                ) | Out-Null
                try { Stop-Transcript | Out-Null } catch {}
                exit
            }
        } catch {
            [System.Windows.MessageBox]::Show(
                "DIAGNOSTICO: Start-Process falhou ao tentar elevar (provavelmente UAC cancelado ou bloqueado por politica).`n`nErro: $($_.Exception.Message)`n`nA ferramenta vai continuar sem privilegios de administrador.",
                "Elevacao opcional", 0, 48
            ) | Out-Null
        }
    }
}

trap {
    [System.Windows.MessageBox]::Show(
        "Erro fatal não tratado:`n`n$($_.Exception.Message)`n`n$($_.ScriptStackTrace)",
        "Erro Fatal - NOC Impressoras", 0, 16
    ) | Out-Null
    Write-SystemLog "ERRO FATAL: $($_.Exception.Message)" -Level Error
    try { Stop-Transcript | Out-Null } catch {}
    exit 1
}

function Write-SystemLog {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        [ValidateSet("Info", "Warning", "Error", "Success", "Dev")]
        [string]$Level = "Info"
    )

    $color = switch ($Level) {
        "Info"    { "Gray" }
        "Warning" { "Yellow" }
        "Error"   { "Red" }
        "Success" { "Green" }
        "Dev"     { "Magenta" }
    }
    
    $prefix = "[$($Level.ToUpper())]"
    Write-Host "$prefix $Message" -ForegroundColor $color

    if ($null -ne $script:txtLoadingLog -and $null -ne $script:logScroll) {
        [System.Windows.Threading.Dispatcher]::CurrentDispatcher.Invoke([System.Action]{
            $script:txtLoadingLog.Text += "`n$prefix $Message"
            $script:logScroll.ScrollToEnd()
        }, [System.Windows.Threading.DispatcherPriority]::Background)
    }

    try {
        if (-not $script:LogFilePath) {
            $logDir = Join-Path $PSScriptRoot "Logs"
            if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
            $script:LogFilePath = Join-Path $logDir "noc-$(Get-Date -Format 'yyyy-MM-dd').log"
        }
        $linha = "$(Get-Date -Format 'HH:mm:ss') $prefix $Message"
        Add-Content -LiteralPath $script:LogFilePath -Value $linha -Encoding UTF8
    } catch {
    }
}

Write-SystemLog "Iniciando Elgin Impressoras v2.0.1 (Single File)..." -Level Info

[System.Windows.Threading.Dispatcher]::CurrentDispatcher.add_UnhandledException({
    param($sender, $e)
    Write-SystemLog "ERRO OCULTO DE RENDERIZAÇÃO" -Level Error
    Write-SystemLog "A interface quebrou ao tentar desenhar os elementos na tela:" -Level Error
    Write-SystemLog "$($e.Exception.Message)" -Level Warning
    if ($e.Exception.InnerException) {
        Write-SystemLog "Detalhe técnico: $($e.Exception.InnerException.Message)" -Level Warning
    }
    Write-SystemLog "O script continuará aberto para você ler o erro acima." -Level Warning
    $e.Handled = $true 
})


# ─────────────────────────────────────────────────────────────────────────────
#  CACHE GLOBAL E FUNÇÕES DE MONITORAMENTO (SNMP E WMI)
# ─────────────────────────────────────────────────────────────────────────────
$script:snmpCacheGlobal = [System.Collections.Concurrent.ConcurrentDictionary[string, object]]::new()

function Get-TonerSNMP {
    param([string]$IP, [int]$Qtd = 1, [string]$Community = "public")
    Write-SystemLog "Consultando IP: $IP (Buscando OID para $Qtd toner/s)..." -Level Warning

    try {
        $udp = New-Object System.Net.Sockets.UdpClient
        $udp.Client.ReceiveTimeout = 1500
        $udp.Connect($IP, 161)

        function Build-SnmpGetBulk {
            param([string[]]$Oids, [int]$MaxRepetitions = 15)
            function ToOidBytes([string]$oid) {
                $parts = $oid.Split('.') | ForEach-Object { [int]$_ }
                $bytes = @(0x2b)
                for ($i = 2; $i -lt $parts.Count; $i++) {
                    $val = $parts[$i]
                    if ($val -lt 128) { $bytes += [byte]$val }
                    else {
                        $buf = @(); $buf += [byte]($val -band 0x7F); $val = $val -shr 7
                        while ($val -gt 0) { $buf = @([byte](($val -band 0x7F) -bor 0x80)) + $buf; $val = $val -shr 7 }
                        $bytes += $buf
                    }
                }
                return $bytes
            }
            $varbinds = @()
            foreach ($oid in $Oids) {
                $oidBytes = ToOidBytes $oid
                $oidTlv   = @(0x06, $oidBytes.Count) + $oidBytes
                $nullTlv  = @(0x05, 0x00)
                $varbinds += @(0x30, ($oidTlv.Count + $nullTlv.Count)) + $oidTlv + $nullTlv
            }
            $varbindListTlv = @(0x30, $varbinds.Count) + $varbinds
            $community = [System.Text.Encoding]::ASCII.GetBytes($Community)
            $commTlv   = @(0x04, $community.Count) + $community
            $reqId     = @(0x02, 0x04, 0x00, 0x00, 0x00, 0x02)
            $nonRep    = @(0x02, 0x01, 0x00)
            $maxRep    = @(0x02, 0x01, [byte]$MaxRepetitions)
            $pdu       = @(0xa5) + @(0x00) + $reqId + $nonRep + $maxRep + $varbindListTlv
            $pdu[1]    = $pdu.Count - 2
            $version   = @(0x02, 0x01, 0x01)  # SNMPv2c (necessario p/ GETBULK)
            $seq       = @(0x30) + @(0x00) + $version + $commTlv + $pdu
            $seq[1]    = $seq.Count - 2
            return [byte[]]$seq
        }

        # Parser BER minimo, generico o suficiente pra decodificar a
        # VarBindList de uma resposta GETBULK (varios OIDs/valores
        # intercalados numa unica resposta, em vez de 1 GET = 1 valor).
        function Read-BerTlv {
            param([byte[]]$data, [int]$pos)
            $tag = $data[$pos]; $pos++
            $len = $data[$pos]; $pos++
            if ($len -band 0x80) {
                $n = $len -band 0x7F; $len = 0
                for ($i = 0; $i -lt $n; $i++) { $len = ($len -shl 8) -bor $data[$pos]; $pos++ }
            }
            return @{ Tag=$tag; Len=$len; ValStart=$pos; NextPos=($pos + $len) }
        }
        function Read-BerOid {
            param([byte[]]$data, [int]$pos, [int]$len)
            $end = $pos + $len
            $first = $data[$pos]; $pos++
            $oid = "$([math]::Floor($first/40)).$($first%40)"
            while ($pos -lt $end) {
                $val = 0
                while ($true) {
                    $b = $data[$pos]; $pos++
                    $val = ($val -shl 7) -bor ($b -band 0x7F)
                    if (-not ($b -band 0x80)) { break }
                }
                $oid += ".$val"
            }
            return $oid
        }
        function Convert-SnmpValueBytes {
            param([byte[]]$b)
            if ($null -eq $b -or $b.Count -eq 0) { return 0 }
            $val = 0; foreach ($x in $b) { $val = ($val -shl 8) -bor $x }
            return $val
        }
        function Parse-SnmpBulkResponse {
            param([byte[]]$data)
            $results = New-Object System.Collections.Generic.List[object]
            try {
                $outer = Read-BerTlv $data 0
                $pos = $outer.ValStart
                $verTlv = Read-BerTlv $data $pos; $pos = $verTlv.NextPos
                $commTlv = Read-BerTlv $data $pos; $pos = $commTlv.NextPos
                $pduTlv = Read-BerTlv $data $pos
                $pos = $pduTlv.ValStart
                $reqIdTlv = Read-BerTlv $data $pos; $pos = $reqIdTlv.NextPos
                $errStatTlv = Read-BerTlv $data $pos; $pos = $errStatTlv.NextPos
                $errIdxTlv = Read-BerTlv $data $pos; $pos = $errIdxTlv.NextPos
                $vbListTlv = Read-BerTlv $data $pos
                $vbPos = $vbListTlv.ValStart
                $vbEnd = $vbListTlv.NextPos
                while ($vbPos -lt $vbEnd) {
                    $vbTlv = Read-BerTlv $data $vbPos
                    $inner = $vbTlv.ValStart
                    $oidTlv = Read-BerTlv $data $inner
                    $oidStr = Read-BerOid $data $oidTlv.ValStart $oidTlv.Len
                    $valTlv = Read-BerTlv $data $oidTlv.NextPos
                    $valBytes = if ($valTlv.Len -gt 0) { $data[$valTlv.ValStart..($valTlv.NextPos - 1)] } else { @() }
                    $results.Add([PSCustomObject]@{ Oid=$oidStr; Type=$valTlv.Tag; Bytes=$valBytes })
                    $vbPos = $vbTlv.NextPos
                }
            } catch {}
            return $results
        }

        function Build-SnmpGet {
            param([string]$oid)
            $oidParts = $oid.Split('.') | ForEach-Object { [int]$_ }
            $oidBytes = @(0x2b)
            for ($i = 2; $i -lt $oidParts.Count; $i++) {
                $val = $oidParts[$i]
                if ($val -lt 128) { $oidBytes += [byte]$val }
                else {
                    $buf = @()
                    $buf += [byte]($val -band 0x7F)
                    $val = $val -shr 7
                    while ($val -gt 0) {
                        $buf = @([byte](($val -band 0x7F) -bor 0x80)) + $buf
                        $val = $val -shr 7
                    }
                    $oidBytes += $buf
                }
            }
            $oidTlv   = @(0x06, $oidBytes.Count) + $oidBytes
            $nullTlv  = @(0x05, 0x00)
            $varBind  = @(0x30, ($oidTlv.Count + $nullTlv.Count)) + $oidTlv + $nullTlv
            $varBinds = @(0x30, $varBind.Count) + $varBind
            $community = [System.Text.Encoding]::ASCII.GetBytes($Community)
            $commTlv  = @(0x04, $community.Count) + $community
            $reqId    = @(0x02, 0x04, 0x00, 0x00, 0x00, 0x01)
            $errStat  = @(0x02, 0x01, 0x00)
            $errIdx   = @(0x02, 0x01, 0x00)
            $pdu      = @(0xa0) + @(0x00) + $reqId + $errStat + $errIdx + $varBinds
            $pdu[1]   = $pdu.Count - 2
            $version  = @(0x02, 0x01, 0x00)
            $seq      = @(0x30) + @(0x00) + $version + $commTlv + $pdu
            $seq[1]   = $seq.Count - 2
            return [byte[]]$seq
        }

        function Parse-SnmpInt {
            param([byte[]]$data)
            if ($null -eq $data -or $data.Count -lt 4) { return $null }
            $result = $null
            $i = 0
            while ($i -lt ($data.Count - 2)) {
                if ($data[$i] -eq 0x02) {
                    $len = $data[$i + 1]
                    if ($len -ge 1 -and $len -le 4 -and ($i + 2 + $len) -le $data.Count) {
                        $val = 0
                        for ($j = 0; $j -lt $len; $j++) {
                            $val = ($val -shl 8) -bor $data[$i + 2 + $j]
                        }
                        if ($i -gt 10) { $result = $val }
                    }
                }
                $i++
            }
            return $result
        }

        function Parse-SnmpString {
            param([byte[]]$data)
            if ($null -eq $data -or $data.Count -lt 12) { return "" }
            $result = ""
            $i = 0
            while ($i -lt ($data.Count - 2)) {
                if ($data[$i] -eq 0x04) {
                    $len = $data[$i + 1]
                    if ($len -gt 0 -and ($i + 2 + $len) -le $data.Count -and $i -gt 10) {
                        $result = [System.Text.Encoding]::ASCII.GetString($data[($i + 2)..($i + 1 + $len)]).Trim()
                    }
                }
                $i++
            }
            return $result
        }

        function Parse-SnmpCounter {
            param([byte[]]$data)
            if ($null -eq $data -or $data.Count -lt 4) { return $null }
            $result = $null
            $i = 0
            while ($i -lt ($data.Count - 2)) {
                if ($data[$i] -eq 0x41 -or $data[$i] -eq 0x02) {
                    $len = $data[$i + 1]
                    if ($len -ge 1 -and $len -le 5 -and ($i + 2 + $len) -le $data.Count) {
                        $val = 0
                        for ($j = 0; $j -lt $len; $j++) { $val = ($val -shl 8) -bor $data[$i + 2 + $j] }
                        if ($i -gt 10) { $result = $val }
                    }
                }
                $i++
            }
            return $result
        }

        $ep = [System.Net.IPEndPoint]::new([System.Net.IPAddress]::Any, 0)

        $uptimeStr = "N/A"
        try {
            $pkgUptime = Build-SnmpGet "1.3.6.1.2.1.1.3.0"
            $udp.Send($pkgUptime, $pkgUptime.Count) | Out-Null
            $respUptime = $udp.Receive([ref]$ep)
            $ticks = $null
            for ($i = 0; $i -lt ($respUptime.Count - 2); $i++) {
                if ($respUptime[$i] -eq 0x43) {
                    $len = $respUptime[$i + 1]
                    if ($len -ge 1 -and $len -le 5 -and ($i + 2 + $len) -le $respUptime.Count) {
                        $val = 0
                        for ($j = 0; $j -lt $len; $j++) { $val = ($val -shl 8) -bor $respUptime[$i + 2 + $j] }
                        $ticks = $val; break
                    }
                }
            }
            if ($null -ne $ticks) {
                $sec = $ticks / 100
                $uptimeStr = "$([math]::Floor($sec/86400))d, $([math]::Floor(($sec%86400)/3600))h, $([math]::Floor(($sec%3600)/60))m"
            }
        } catch {}

        $pageCount = $null
        try {
            $pkgPagCount = Build-SnmpGet "1.3.6.1.2.1.43.10.2.1.4.1.1"
            $udp.Send($pkgPagCount, $pkgPagCount.Count) | Out-Null
            $pageCount = Parse-SnmpCounter ($udp.Receive([ref]$ep))
        } catch {}

        $candidatos = @()
        $bulkOk = $false
        try {
            $colNivel = "1.3.6.1.2.1.43.11.1.1.9.1"
            $colMax   = "1.3.6.1.2.1.43.11.1.1.8.1"
            $colDesc  = "1.3.6.1.2.1.43.11.1.1.6.1"
            $pkgBulk = Build-SnmpGetBulk -Oids @($colNivel, $colMax, $colDesc) -MaxRepetitions 15
            $udp.Send($pkgBulk, $pkgBulk.Count) | Out-Null
            $respBulk = $udp.Receive([ref]$ep)
            $vbs = @(Parse-SnmpBulkResponse $respBulk)

            if ($vbs.Count -ge 3 -and ($vbs.Count % 3) -eq 0) {
                $bulkOk = $true
                for ($g = 0; $g -lt $vbs.Count; $g += 3) {
                    $vNivel = $vbs[$g]; $vMax = $vbs[$g+1]; $vDesc = $vbs[$g+2]
                    if ($vNivel.Oid -notlike "$colNivel.*" -or $vMax.Oid -notlike "$colMax.*") { break }
                    if ($vNivel.Type -in @(0x80,0x81,0x82) -or $vMax.Type -in @(0x80,0x81,0x82)) { break }

                    $nivel  = Convert-SnmpValueBytes $vNivel.Bytes
                    $maximo = Convert-SnmpValueBytes $vMax.Bytes
                    $desc   = if ($vDesc.Type -eq 0x04) { [System.Text.Encoding]::ASCII.GetString($vDesc.Bytes).Trim() } else { "" }
                    $indice = [int]($vNivel.Oid.Substring($colNivel.Length + 1))

                    if ($maximo -le 0) { continue }
                    if ($desc -match "(?i)waste|descarte|lixeira|recovery|container|cleaner") { continue }

                    $pct = [math]::Min(100, [math]::Max(0, [math]::Round(($nivel / $maximo) * 100)))

                    $cor = "Preto"
                    if      ($desc -match "(?i)cyan|ciano|azul|\bc\b")       { $cor = "Ciano" }
                    elseif  ($desc -match "(?i)magenta|rosa|\bm\b")           { $cor = "Magenta" }
                    elseif  ($desc -match "(?i)yellow|amarelo|\by\b")         { $cor = "Amarelo" }
                    elseif  ($desc -match "(?i)black|preto|negro|\bk\b")      { $cor = "Preto" }
                    elseif  ($Qtd -gt 1) {
                        switch ($indice % 4) { 1{$cor="Ciano"} 2{$cor="Magenta"} 3{$cor="Amarelo"} 0{$cor="Preto"} }
                    }

                    $candidatos += [PSCustomObject]@{ Indice=$indice; Pct=$pct; CorToner=$cor; Maximo=$maximo }
                }
                Write-SystemLog "GETBULK OK em $IP - $($candidatos.Count) suprimento(s) em 1 round-trip." -Level Dev
            }
        } catch { $bulkOk = $false }

        # Fallback: agente so fala SNMPv1 (sem GETBULK) ou GETBULK falhou -
        # volta pro walk sequencial classico (GET por indice), mais lento
        # mas compativel com qualquer agente SNMP.
        if (-not $bulkOk) {
            Write-SystemLog "GETBULK indisponivel em $IP - usando fallback sequencial (SNMPv1)." -Level Dev
            $candidatos = @()
            $falhasConsecutivas = 0
            foreach ($indice in 1..20) {
                try {
                    $pkgNivel = Build-SnmpGet "1.3.6.1.2.1.43.11.1.1.9.1.$indice"
                    $udp.Send($pkgNivel, $pkgNivel.Count) | Out-Null
                    $nivel = Parse-SnmpInt ($udp.Receive([ref]$ep))

                    $pkgMax = Build-SnmpGet "1.3.6.1.2.1.43.11.1.1.8.1.$indice"
                    $udp.Send($pkgMax, $pkgMax.Count) | Out-Null
                    $maximo = Parse-SnmpInt ($udp.Receive([ref]$ep))

                    if ($null -ne $nivel -and $null -ne $maximo -and $maximo -gt 0) {
                        $falhasConsecutivas = 0
                        $pkgDesc = Build-SnmpGet "1.3.6.1.2.1.43.11.1.1.6.1.$indice"
                        $udp.Send($pkgDesc, $pkgDesc.Count) | Out-Null
                        $desc = Parse-SnmpString ($udp.Receive([ref]$ep))

                        if ($desc -match "(?i)waste|descarte|lixeira|recovery|container|cleaner") { continue }

                        $pct = [math]::Min(100, [math]::Max(0, [math]::Round(($nivel / $maximo) * 100)))

                        $cor = "Preto"
                        if      ($desc -match "(?i)cyan|ciano|azul|\bc\b")       { $cor = "Ciano" }
                        elseif  ($desc -match "(?i)magenta|rosa|\bm\b")           { $cor = "Magenta" }
                        elseif  ($desc -match "(?i)yellow|amarelo|\by\b")         { $cor = "Amarelo" }
                        elseif  ($desc -match "(?i)black|preto|negro|\bk\b")      { $cor = "Preto" }
                        elseif  ($Qtd -gt 1) {
                            switch ($indice % 4) { 1{$cor="Ciano"} 2{$cor="Magenta"} 3{$cor="Amarelo"} 0{$cor="Preto"} }
                        }

                        $candidatos += [PSCustomObject]@{ Indice=$indice; Pct=$pct; CorToner=$cor; Maximo=$maximo }
                    } else {
                        $falhasConsecutivas++
                    }
                } catch {
                    $falhasConsecutivas++
                }
                if ($Qtd -eq 1 -and $candidatos.Count -ge 1) { break }
                if ($Qtd -gt 1 -and $candidatos.Count -ge 8) { break }
                if ($falhasConsecutivas -ge 3) {
                    Write-SystemLog "SNMP sem resposta em $IP após $falhasConsecutivas tentativas — abortando busca de toner." -Level Dev
                    break
                }
            }
        }

        $melhores = @()
        if ($candidatos.Count -gt 0) {
            if ($Qtd -gt 1) {
                $pesos = @{ "Ciano"=1; "Magenta"=2; "Amarelo"=3; "Preto"=4 }
                $melhores = $candidatos | Group-Object CorToner | ForEach-Object { $_.Group | Select-Object -First 1 } | Sort-Object { $pesos[$_.CorToner] }
            } else {
                $melhores = $candidatos | Sort-Object Maximo -Descending | Select-Object -First 1
            }
        }

        $udp.Dispose()
        return @{ Toners=$melhores; Uptime=$uptimeStr; PageCount=$pageCount }
    } catch {
        if ($null -ne $udp) { $udp.Dispose() }
        return @{ Toners=$null; Uptime="Erro"; PageCount=$null }
    }
}

function Obter-Modelo {
    param([string]$Driver)
    switch -Regex ($Driver) {
        "P 311"     { "Ricoh P311" }
        "P 502"     { "Ricoh P502" }
        "M3040"     { "Kyocera M3040idn" }
        "P3055"     { "Kyocera P3055dn" }
        "M6530"     { "Kyocera M6530cdn" }
        "Honeywell" { "Honeywell RP4f" }
        "TT042"     { "Elgin TT042" }
        "ELGIN"     { "Elgin TT042 Plus" }
        default     { $Driver -replace '\s+(PCL\d*|PS|KX|XPS|UFR\s*II|Class Driver)\b.*', '' }
    }
}

# Classifica a impressora em A4 / Etiqueta / Portatil pelo Nome+Modelo
# (mesmo criterio ja usado no resto do sistema pra separar etiquetadoras,
# ex.: -match "TT042|Honeywell" em Get-ImpressorasEmpresa). Etiqueta e
# Portatil sao checadas antes de A4 porque marcas como Elgin/Honeywell
# tambem aparecem em nomes de servidor que poderiam falsamente casar com
# termos genericos de impressora de folha.
function Obter-TipoImpressora {
    param([string]$Nome, [string]$Modelo)
    $texto = "$Nome $Modelo"
    switch -Regex ($texto) {
        "(?i)zebra|elgin|tt042|argox"               { "Etiqueta"; break }
        "(?i)honeywell|rp4f|sewoo|portatil|portátil" { "Portatil"; break }
        "(?i)canon|kyocera|ricoh|pantum|hp\b|epson|brother|xerox|lexmark|samsung" { "A4"; break }
        default { "A4" }
    }
}

# ─────────────────────────────────────────────────────────────────────────────
#  NOTIFICAÇÃO FLUTUANTE (TOAST)
# ─────────────────────────────────────────────────────────────────────────────
function Show-ToastNotification {
    param(
        [string]$Mensagem,
        [string]$Tipo = "Sucesso",
        [System.Windows.Window]$JanelaPai
    )

    $corBorda = if ($Tipo -eq "Erro") { "#EF4444" } else { "#10B981" }
    $icone    = if ($Tipo -eq "Erro") { "❌" } else { "✅" }

    # O truque aqui: a janela principal do Toast é invisível, e o Border que tem a cor é alinhado no fundo (Bottom)
    $toastXaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        WindowStyle="None" AllowsTransparency="True" Background="Transparent"
        Topmost="True" ShowInTaskbar="False" ResizeMode="NoResize"
        WindowStartupLocation="CenterOwner">
    <Grid>
        <Border Background="#27272A" BorderBrush="$corBorda" BorderThickness="4,0,0,0" CornerRadius="6" 
                Margin="0,0,0,15" HorizontalAlignment="Center" VerticalAlignment="Bottom" Height="65" Width="320">
            <Border.Effect>
                <DropShadowEffect BlurRadius="8" Opacity="0.4" ShadowDepth="2" Direction="270" />
            </Border.Effect>
            <Grid Margin="12,0">
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="Auto"/>
                    <ColumnDefinition Width="*"/>
                </Grid.ColumnDefinitions>
                <TextBlock Grid.Column="0" Text="$icone" FontSize="16" VerticalAlignment="Center" Margin="0,0,10,0"/>
                <TextBlock Grid.Column="1" Text="$Mensagem" Foreground="White" FontSize="12" FontWeight="SemiBold" VerticalAlignment="Center" TextWrapping="Wrap"/>
            </Grid>
        </Border>
    </Grid>
</Window>
"@
    
    try {
        $toastWindow = [Windows.Markup.XamlReader]::Load([System.Xml.XmlReader]::Create([System.IO.StringReader]::new($toastXaml)))
        
        # Copia o tamanho do Card para amarrar o popup invisível por cima dele perfeitamente
        if ($null -ne $JanelaPai) {
            $toastWindow.Owner = $JanelaPai
            $toastWindow.Width = $JanelaPai.Width
            $toastWindow.Height = $JanelaPai.Height
        } else {
            $toastWindow.Width = 450; $toastWindow.Height = 450
        }

        $timer = New-Object System.Windows.Threading.DispatcherTimer
        $timer.Interval = [TimeSpan]::FromSeconds(3)
        $timer.Add_Tick({
            $toastWindow.Close()
            $timer.Stop()
        }.GetNewClosure())

        $toastWindow.Show()
        $timer.Start()
    } catch {
        Write-SystemLog "Falha ao exibir toast notification: $_" -Level Warning
    }
}

# ─────────────────────────────────────────────────────────────────────────────
#  FUNÇÃO WEBHOOK - TEAMS
# ─────────────────────────────────────────────────────────────────────────────
function Send-AlertaWebhook {
    param(
        [string]$Impressora,
        [string]$Modelo,
        [array]$ListaToners, # Array com propriedades: Cor e Nivel
        [bool]$Manual = $false
    )

    $Webhook = $script:Config.WebhookUrl
    if ([string]::IsNullOrWhiteSpace($Webhook)) { return $false }

    $titulo = if ($Manual) { "AVISO MANUAL DE TONER" } else { "ALERTA CRITICO DE TONER" }
    $corTitulo = if ($Manual) { "Good" } else { "Attention" }
    $msgIntro = if ($Manual) { 
        "Um alerta de suprimento foi disparado manualmente a partir do NOC." 
    } else { 
        "Foi detectado um nivel muito baixo de suprimento em uma das impressoras monitoradas (5% ou menos). A substituicao e recomendada em breve para evitar interrupcoes." 
    }

    # Constrói os fatos dinamicamente (1 cor vs Múltiplas cores)
    $facts = @( @{ title = "Equipamento:"; value = "$Modelo ($Impressora)" } )
    
    if ($Manual) {
        foreach ($t in $ListaToners) {
            $facts += @{ title = "Nivel $($t.Cor):"; value = "**$($t.Nivel)**" }
        }
    } else {
        $facts += @{ title = "Cor do Toner:"; value = $ListaToners[0].Cor }
        $facts += @{ title = "Nivel Atual:"; value = "**$($ListaToners[0].Nivel)**" }
    }
    
    $facts += @{ title = "Data do Alerta:"; value = "$(Get-Date -Format 'dd/MM/yyyy HH:mm')" }

    $BodyObj = @{
        type = "message"
        attachments = @(
            @{
                contentType = "application/vnd.microsoft.card.adaptive"
                content = @{
                    "`$schema" = "http://adaptivecards.io/schemas/adaptive-card.json"
                    type = "AdaptiveCard"
                    version = "1.4"
                    msteams = @{ width = "Full" }
                    body = @(
                        @{
                            type = "Container"
                            style = if ($Manual) { "good" } else { "attention" }
                            items = @( @{ type = "TextBlock"; text = $titulo; weight = "Bolder"; size = "Large"; color = $corTitulo } )
                        },
                        @{ type = "TextBlock"; text = $msgIntro; wrap = $true; spacing = "Medium" },
                        @{ type = "FactSet"; spacing = "Medium"; facts = $facts }
                    )
                }
            }
        )
    } 
    
    $JsonBody = $BodyObj | ConvertTo-Json -Depth 10
    $Bytes = [System.Text.Encoding]::UTF8.GetBytes($JsonBody)

    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-RestMethod -Uri $Webhook -Method POST -ContentType "application/json; charset=utf-8" -Body $Bytes | Out-Null
        Write-SystemLog "Webhook enviado com sucesso: $Impressora" -Level Success
        return $true
    } catch {
        Write-SystemLog "Falha ao enviar Webhook: $($_.Exception.Message)" -Level Error
        return $false
    }
}

function Get-ImpressorasEmpresa {
    $servidor = $script:Config.ServidorPrint
    if ($script:txtStatusLoading) { $script:txtStatusLoading.Text = "Conectando ao RPC do Servidor..." }
    Write-SystemLog "Abrindo canal de comunicação RPC com '$servidor'..." -Level Info
    
    [System.Windows.Threading.Dispatcher]::CurrentDispatcher.Invoke([System.Action]{}, [System.Windows.Threading.DispatcherPriority]::Render)

    Write-SystemLog "Iniciando coleta de dados no servidor: '$servidor'..." -Level Info
    try {
        if ($null -ne $script:Config.ModoOffline -and $script:Config.ModoOffline -eq $true) {
            Write-SystemLog "Modo Offline forçado no config. Pulando RPC e varredura..." -Level Dev
            throw "Modo_Offline_Forcado"
        }

        Write-SystemLog "Mapeando tabelas de portas (Get-PrinterPort)..." -Level Info
        [System.Windows.Threading.Dispatcher]::CurrentDispatcher.Invoke([System.Action]{}, [System.Windows.Threading.DispatcherPriority]::Render)
        
        $ports    = Get-PrinterPort -ComputerName $servidor -ErrorAction Stop

        Write-SystemLog "Sucesso! Extraindo spool de impressoras publicadas (Get-Printer)..." -Level Success
        [System.Windows.Threading.Dispatcher]::CurrentDispatcher.Invoke([System.Action]{}, [System.Windows.Threading.DispatcherPriority]::Render)
        
        $printers = Get-Printer    -ComputerName $servidor -ErrorAction Stop

        return Process-ImpressorasList -printers $printers -ports $ports -servidor $servidor
    } catch {
        Write-SystemLog "Servidor inacessível ou Modo Offline forçado. Carregando dados de contingência..." -Level Error
        
        $dadosJson = $script:mockJson | ConvertFrom-Json
        $bc = [System.Windows.Media.BrushConverter]::new()
        $listaMock = [System.Collections.Generic.List[object]]::new()
        
        $totalMock = $dadosJson.Count
        $countMock = 0
        
        foreach ($imp in $dadosJson) {
            $countMock++
            Write-SystemLog "Sincronizando mock: $($imp.Nome)" -Level Info

            if ($script:loadingBar) {
                $p = [math]::Round(($countMock / $totalMock) * 100)
                $script:loadingBar.Value = $p
                $script:txtPorcentagem.Text = "$p%"
            }
            [System.Windows.Threading.Dispatcher]::CurrentDispatcher.Invoke([System.Action]{}, [System.Windows.Threading.DispatcherPriority]::Background)

            $subToners = [System.Collections.Generic.List[object]]::new()
            if ($imp.Nome -match 'TT042|Honeywell|Etiqueta|Elgin|Honey|Sewoo') {
                $subToners.Add([PSCustomObject]@{
                    Valor    = "N/A"
                    Vis      = [System.Windows.Visibility]::Visible
                    Width    = 0.0
                    MaxWidth = 80.0
                    Cor      = $bc.ConvertFromString("#9CA3AF")
                }) | Out-Null
            } else {
                foreach ($t in $imp.Toners) {
                    $pct    = [int]($t.Pct -replace '%', '')
                    $corHex = switch ($t.Cor) { "Ciano"{"#00BCFF"} "Magenta"{"#EC4899"} "Amarelo"{"#EAB308"} "Preto"{"#F4F4F5"} default{"#219AF9"} }
                    $sigla  = switch ($t.Cor) { "Ciano"{"C"} "Magenta"{"M"} "Amarelo"{"Y"} "Preto"{"P"} default{""} }
                    $bw     = if ($imp.Toners.Count -eq 1) { 80.0 } else { 35.0 }
                    $subToners.Add([PSCustomObject]@{
                        Valor    = if ($sigla -ne "") { "${sigla}:${pct}%" } else { "${pct}%" }
                        Vis      = [System.Windows.Visibility]::Visible
                        Width    = [double]([math]::Round(($pct / 100.0) * $bw))
                        MaxWidth = $bw
                        Cor      = $bc.ConvertFromString($corHex)
                    }) | Out-Null
                }
            }
            
            $listaMock.Add([PSCustomObject]@{
                Nome=$imp.Nome; IP=$imp.IP; Modelo=$imp.Modelo
                ListaToners=$subToners; Status=$imp.Status; Uptime="12d, 4h"; MacAddress="N/A"
                PageCount="N/A"
            }) | Out-Null
        }
        return $listaMock
    }
}

function Process-ImpressorasList {
    param($printers, $ports, $servidor)
    $bc = New-Object System.Windows.Media.BrushConverter

    $portMap = @{}
    if ($null -ne $ports) {
        foreach ($port in $ports) {
            if ($port.Name) { $portMap[$port.Name] = [string]$port.PrinterHostAddress }
        }
    }

    $pool = [runspacefactory]::CreateRunspacePool(1, 30)
    $pool.Open()

    $defGetToner = (Get-Command Get-TonerSNMP).Definition
    $defObterMod = (Get-Command Obter-Modelo).Definition

    $tasks = @()
    foreach ($printer in $printers) {
        $ps = [powershell]::Create()
        $ps.RunspacePool = $pool
        [void]$ps.AddScript(@"
param(`$p, `$portMap, `$snmpCache, `$defGetToner, `$defObterMod, `$snmpCommunity)

Invoke-Expression "function Get-TonerSNMP { `$defGetToner }"
Invoke-Expression "function Obter-Modelo { `$defObterMod }"

`$ip     = if (`$portMap.ContainsKey(`$p.PortName)) { `$portMap[`$p.PortName] } else { `$p.PortName }
`$online = `$false
if (`$ip -match '^\d') {
    try { if ((New-Object System.Net.NetworkInformation.Ping).Send(`$ip, 400).Status -eq 'Success') { `$online = `$true } } catch {}
}
`$modelo = Obter-Modelo `$p.DriverName
`$qtd    = if (`$modelo -match 'color|M6530' -or `$p.Name -match 'color') { 4 } else { 1 }
`$snmp   = @{ Toners = `$null; Uptime = 'N/A' }

if (`$online -and `$modelo -notmatch 'TT042|Honeywell' -and `$p.Name -notmatch 'TT042|Honeywell|Etiqueta|Elgin') {
    `$cached = `$null
    if (-not `$snmpCache.TryGetValue(`$ip, [ref]`$cached)) {
        `$cached = Get-TonerSNMP -IP `$ip -Qtd `$qtd -Community `$snmpCommunity
        `$snmpCache.TryAdd(`$ip, `$cached) | Out-Null
    }
    `$snmp = `$cached
}

return [PSCustomObject]@{
    Nome      = `$p.Name
    IP        = `$ip
    Modelo    = `$modelo
    Status    = if (`$online) { 'Online' } else { 'Offline' }
    Qtd       = `$qtd
    Raw       = `$snmp.Toners
    Uptime    = `$snmp.Uptime
    PageCount = `$snmp.PageCount
}
"@)
        [void]$ps.AddArgument($printer)
        [void]$ps.AddArgument($portMap)
        [void]$ps.AddArgument($script:snmpCacheGlobal)
        [void]$ps.AddArgument($defGetToner)
        [void]$ps.AddArgument($defObterMod)
        [void]$ps.AddArgument($script:Config.SnmpCommunity)
        $tasks += @{ Pipe=$ps; Handle=$ps.BeginInvoke() }
    }

    $final = [System.Collections.Generic.List[object]]::new()
    $totalTarefas = $tasks.Count
    $processados = 0

    if ($script:txtStatusLoading) { $script:txtStatusLoading.Text = "Varrendo Linhas Paralelas..." }

    foreach ($t in $tasks) {
        $processados++
        
        [System.Windows.Threading.Dispatcher]::CurrentDispatcher.Invoke([System.Action]{}, [System.Windows.Threading.DispatcherPriority]::Background)

        try {
            $obj = $t.Pipe.EndInvoke($t.Handle) | Select-Object -Last 1
            if ($null -ne $obj) {
                Write-SystemLog "Mapeado: $($obj.Nome) -> $($obj.Status) ($processados/$totalTarefas)" -Level Info
                
                if ($script:loadingBar -and $script:txtLoadingLog) {
                    $pctAtual = [math]::Round(($processados / $totalTarefas) * 100)
                    $script:loadingBar.Value = $pctAtual
                    $script:txtPorcentagem.Text = "$pctAtual%"
                    $script:logScroll.ScrollToEnd()
                }

                $lista = [System.Collections.Generic.List[object]]::new()
                if ($obj.Nome -match 'TT042|Honeywell|Etiqueta|Elgin') {
                    $lista.Add([PSCustomObject]@{
                        Valor    = "N/A"
                        Vis      = [System.Windows.Visibility]::Visible
                        Width    = 0.0
                        MaxWidth = 80.0
                        Cor      = $bc.ConvertFromString("#9CA3AF")
                    }) | Out-Null
                }
                elseif ($obj.Status -eq 'Online' -and $null -ne $obj.Raw -and @($obj.Raw).Count -gt 0) {
                    $bw = if ($obj.Qtd -eq 1) { 80.0 } else { 35.0 }
                    foreach ($r in @($obj.Raw)) {
                        $corHex = switch ($r.CorToner) { "Ciano"{"#00BCFF"} "Magenta"{"#EC4899"} "Amarelo"{"#EAB308"} "Preto"{"#F4F4F5"} default{"#219AF9"} }
                        $sigla  = switch ($r.CorToner) { "Ciano"{"C"} "Magenta"{"M"} "Amarelo"{"Y"} "Preto"{"K"} default{""} }
                        $lista.Add([PSCustomObject]@{
                            Valor    = if ($sigla -ne "") { "${sigla}:$($r.Pct)%" } else { "$($r.Pct)%" }
                            Vis      = [System.Windows.Visibility]::Visible
                            Width    = [double]([math]::Round(($r.Pct / 100.0) * $bw))
                            MaxWidth = $bw
                            Cor      = $bc.ConvertFromString($corHex)
                        }) | Out-Null
                    }
                } else {
                    $lista.Add([PSCustomObject]@{
                        Valor    = "--"
                        Vis      = [System.Windows.Visibility]::Collapsed
                        Width    = 0.0
                        MaxWidth = 0.0
                        Cor      = $bc.ConvertFromString("#9CA3AF")
                    }) | Out-Null
                }
                
                $final.Add([PSCustomObject]@{
                    Nome=$obj.Nome; IP=$obj.IP; Modelo=$obj.Modelo
                    ListaToners=$lista; Status=$obj.Status; Uptime=$obj.Uptime; MacAddress="N/A"
                    PageCount=$(if ($obj.PageCount) { "{0:N0}" -f $obj.PageCount } else { "N/A" })
                }) | Out-Null
            }
        } catch {
            Write-Warning "Runspace error: $_"
        }
        $t.Pipe.Dispose()
    }
    $pool.Close(); $pool.Dispose()
    return $final
}

# ─────────────────────────────────────────────────────────────────────────────
#  FUNÇÕES DE GERENCIAMENTO DE DRIVERS
# ─────────────────────────────────────────────────────────────────────────────
function Show-DriverPopup {
    param([string]$nomeImpressora, [string]$modeloImpressora, [string]$ipImpressora)

    $pastaDrivers = Join-Path $PSScriptRoot "..\Drivers"
    $pastaDrivers = [System.IO.Path]::GetFullPath($pastaDrivers)
    
    $servidorPrint = $script:Config.ServidorPrint
    $faixaRede     = $script:Config.FaixaRedeLocal

    $ehEtiqueta = $modeloImpressora -match "(?i)TT042|Honeywell|RP4f|ELGIN|Zebra|Argox" -or $nomeImpressora -match "(?i)etiqueta|zebra|argox|TT042|Honey"
    $ehImpressoraRedeServidor = ($ipImpressora -match "^$([regex]::Escape($faixaRede))") -and (-not $ehEtiqueta)

    $arquivoDriver = $null

    if (-not $ehImpressoraRedeServidor -and $script:Config.DriverMap) {
        $mapeado = $script:Config.DriverMap | Where-Object { $nomeImpressora -like $_.nome } | Select-Object -First 1
        if ($mapeado) {
            $caminhoMapeado = Join-Path $pastaDrivers $mapeado.arquivo
            if (Test-Path $caminhoMapeado) {
                $arquivoDriver = Get-Item $caminhoMapeado
                Write-SystemLog "Driver resolvido via DriverMap: $($mapeado.nome) -> $($mapeado.arquivo)" -Level Success
            } else {
                Write-SystemLog "DriverMap aponta pra '$($mapeado.arquivo)' mas o arquivo não existe. Caindo pro fallback." -Level Warning
            }
        }
    }

    function Resolve-WindowsShortcut {
        param([string]$lnkPath)
        try {
            $wsh = New-Object -ComObject WScript.Shell
            return $wsh.CreateShortcut($lnkPath).TargetPath
        } catch { return $null }
    }

    if (-not $arquivoDriver -and (Test-Path $pastaDrivers)) {
        $rotasBusca = [System.Collections.Generic.List[string]]::new()
        $rotasBusca.Add($pastaDrivers) | Out-Null

        Get-ChildItem -Path $pastaDrivers -Filter "*.lnk" | ForEach-Object {
            $target = Resolve-WindowsShortcut $_.FullName
            if ($target -and (Test-Path $target)) { $rotasBusca.Add($target) | Out-Null }
        }

        $allFiles = foreach ($rota in $rotasBusca) {
            Get-ChildItem -Path $rota -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Extension -match '(?i)^\.(inf|exe)$' }
        }
        
        if ($ehEtiqueta) {
            $etiquetaFiles = $allFiles | Where-Object { $_.FullName -match "TT042" -or $_.FullName -match "Elgin" -or $_.FullName -match "Honeywell" }
            
            if ($nomeImpressora -match "50" -or $modeloImpressora -match "50") {
                $arquivoDriver = $etiquetaFiles | Where-Object { $_.FullName -match "50" } | Select-Object -First 1
            } elseif ($nomeImpressora -match "Plus" -or $modeloImpressora -match "Plus") {
                $arquivoDriver = $etiquetaFiles | Where-Object { $_.FullName -match "Plus" } | Select-Object -First 1
            }
            if ($null -eq $arquivoDriver) { $arquivoDriver = $etiquetaFiles | Select-Object -First 1 }
            if ($null -eq $arquivoDriver) { $arquivoDriver = $allFiles | Select-Object -First 1 }
        } else {
            $numeroPadrao = ""
            if ($modeloImpressora -match "(\d+)") { $numeroPadrao = $Matches[1] }
            $arquivoDriver = $allFiles | Where-Object {
                $_.FullName -match [regex]::Escape($modeloImpressora) -or
                $_.Directory.Name -match [regex]::Escape($modeloImpressora) -or
                ($numeroPadrao -ne "" -and $_.FullName -match $numeroPadrao)
            } | Select-Object -First 1
        }
    }

    $marca = ""
    if ($modeloImpressora -match "(Ricoh|Kyocera|Elgin|Honeywell)") { $marca = $Matches[1] }
    $numero = ""
    if ($modeloImpressora -match "(\d+)") { $numero = $Matches[1] }

    $txtInstalado = "Nenhum driver ou mapeamento localizado localmente."
    $corStatus = "#F59E0B" 

    try {
        $impressoraPronta = Get-Printer | Where-Object { $_.Name -like "*$nomeImpressora*" -or $_.ConnectionName -like "*$nomeImpressora*" }
        
        if ($impressoraPronta) {
            $txtInstalado = "Impressora já instalada e pronta para uso."
            $corStatus = "#219AF9"
        } else {
            $driverInstalado = Get-PrinterDriver | Where-Object {
                $target = $_.Name
                if ($ehEtiqueta) {
                    $target -match "TT042" -or ($target -match "Elgin" -and $target -match "042") -or $target -like "*$marca*"
                } else {
                    ($marca -eq "" -or $target -like "*$marca*") -and ($numero -eq "" -or $target -like "*$numero*")
                }
            } | Select-Object -First 1
            
            if (-not $driverInstalado -and $marca -ne "") {
                $driverInstalado = Get-PrinterDriver | Where-Object {
                    $_.Name -like "*$marca*" -and ($_.Name -match "(?i)Universal|Class|KX|Classic|Mono|Color")
                } | Select-Object -First 1
            }

            if ($driverInstalado) { 
                $txtInstalado = "Driver pré-instalado: $($driverInstalado.Name)" 
                $corStatus = "#219AF9" 
            }
        }
    } catch {
        $txtInstalado = "Serviço de Spooler do Windows indisponível."
        $corStatus = "#F75C5C" 
    }
    
    $txtComoInstalar = if ($ehImpressoraRedeServidor) {
        "Dispositivo gerenciado via servidor. Clique em 'Mapear via Rede' para abrir o assistente de conexão nativo do Windows."
    } elseif ($arquivoDriver) { 
        $arquivoDriver.FullName 
    } else { 
        "Nenhum pacote automático (.inf ou .exe) localizado. Clique abaixo para selecionar manualmente." 
    }

    try {
        $popupReader = [System.Xml.XmlReader]::Create([System.IO.StringReader]::new($script:driverPopupXaml))
        $popup       = [Windows.Markup.XamlReader]::Load($popupReader)
        if ($window -and $window.IsVisible) { $popup.Owner = $window }
        
        $popup.FindName("TxtNome").Text   = $nomeImpressora
        $popup.FindName("TxtModelo").Text = "Driver Necessário: $modeloImpressora"
        
        $lblStatus = $popup.FindName("TxtStatusDriver")
        $lblStatus.Text = $txtInstalado
        $lblStatus.Foreground = [System.Windows.Media.BrushConverter]::new().ConvertFromString($corStatus)
        
        $popup.FindName("TxtInstrucao").Text = $txtComoInstalar

        $btnAcao   = $popup.FindName("BtnAcao")
        $btnFechar = $popup.FindName("BtnFechar")
        $btnFecharX = $popup.FindName("BtnFecharX")
        $pnlCabecalho = $popup.FindName("PnlCabecalho")
        $btnFecharX.Add_Click({ $popup.Close() })
        $pnlCabecalho.Add_MouseLeftButtonDown({ $popup.DragMove() })

        if ($ehImpressoraRedeServidor) {
            $btnAcao.Content = "Mapear via Rede"
            $btnAcao.Background = [System.Windows.Media.BrushConverter]::new().ConvertFromString("#219AF9")
            $btnAcao.Add_Click({
                try {
                    $uncPath = "\\$servidorPrint\$nomeImpressora"
                    Start-Process "rundll32.exe" -ArgumentList "printui.dll,PrintUIEntry /in /n `"$uncPath`""
                    $popup.Close()
                } catch {
                    [System.Windows.MessageBox]::Show("Falha ao invocar o assistente de conexão do Windows: $_", "Erro de Processo", 0, 16)
                }
            })
        } elseif ($arquivoDriver) {
            $filePath = $arquivoDriver.FullName
            
            if ($arquivoDriver.Extension -eq ".exe") {
                $btnAcao.Content = "Executar (.EXE)"
                $btnAcao.Background = [System.Windows.Media.BrushConverter]::new().ConvertFromString("#219AF9")
                $btnAcao.Add_Click({
                    if (-not $script:IsElevated) {
                        [System.Windows.MessageBox]::Show("Requer Administrador. Reabra a ferramenta como Administrador para instalar drivers.", "Permissao necessaria", 0, 48) | Out-Null
                        return
                    }
                    try {
                        $proc = Start-Process "$filePath" -Wait -PassThru
                        if ($proc.ExitCode -eq 0 -or $null -eq $proc.ExitCode) {
                            [System.Windows.MessageBox]::Show("Instalador interativo executado com sucesso!", "Concluído", 0, 64)
                            $popup.Close()
                        } else {
                            [System.Windows.MessageBox]::Show("O instalador retornou um código de saída incomum: $($proc.ExitCode)", "Aviso", 0, 48)
                        }
                    } catch {
                        [System.Windows.MessageBox]::Show("Falha ao executar instalador executável: $_", "Erro de Execução", 0, 16)
                    }
                })
            } else {
                $btnAcao.Content = "Injetar Driver (.INF)"
                $btnAcao.Background = [System.Windows.Media.BrushConverter]::new().ConvertFromString("#219AF9")
                $btnAcao.Add_Click({
                    if (-not $script:IsElevated) {
                        [System.Windows.MessageBox]::Show("Requer Administrador. Reabra a ferramenta como Administrador para instalar drivers.", "Permissao necessaria", 0, 48) | Out-Null
                        return
                    }
                    try {
                        $proc = Start-Process "pnputil.exe" -ArgumentList "/add-driver `"$filePath`" /install" -Wait -PassThru
                        if ($proc.ExitCode -eq 0) {
                            [System.Windows.MessageBox]::Show("Driver adicionado e injetado com sucesso!", "Concluído", 0, 64)
                            $popup.Close()
                        } else {
                            [System.Windows.MessageBox]::Show("O Windows recusou o pacote do driver. Código: $($proc.ExitCode)", "Falha", 0, 48)
                        }
                    } catch {
                        [System.Windows.MessageBox]::Show("Falha ao executar PnPUtil: $_", "Erro Pnputil", 0, 16)
                    }
                })
            }
        } elseif ($ehEtiqueta) {
            $btnAcao.Content = "Procurar .INF/.EXE Manual..."
            $btnAcao.Background = [System.Windows.Media.BrushConverter]::new().ConvertFromString("#F59E0B")
            $btnAcao.IsEnabled = $true
            $btnAcao.Opacity = 1.0
            $btnAcao.Add_Click({
                $ofd = New-Object Microsoft.Win32.OpenFileDialog
                $ofd.Filter = "Pacotes de Instalação (*.inf; *.exe)|*.inf;*.exe"
                $ofd.Title = "Selecionar Driver Manual para $modeloImpressora"
                if ($ofd.ShowDialog() -eq $true) {
                    try {
                        $manualPath = $ofd.FileName
                        if ($manualPath -match "\.exe$") {
                            Start-Process "$manualPath" -Wait
                            [System.Windows.MessageBox]::Show("Instalador manual executado com sucesso!", "Concluído", 0, 64)
                        } else {
                            $proc = Start-Process "pnputil.exe" -ArgumentList "/add-driver `"$manualPath`" /install" -Wait -PassThru
                            if ($proc.ExitCode -eq 0) { [System.Windows.MessageBox]::Show("Driver manual injetado!", "Concluído", 0, 64) }
                        }
                        $popup.Close()
                    } catch {
                        [System.Windows.MessageBox]::Show("Falha ao instalar arquivo manual: $_", "Erro Técnico", 0, 16)
                    }
                }
            })
        } else {
            $btnAcao.IsEnabled = $false
            $btnAcao.Opacity   = 0.3
            $btnAcao.Content   = "Indisponível"
        }

        $btnFechar.Add_Click({ $popup.Close() })
        $popup.ShowDialog() | Out-Null
    } catch {
        [System.Windows.MessageBox]::Show("Erro crítico ao inicializar o subsistema de drivers: $_", "Erro de Arquitetura")
    }
}


# ─────────────────────────────────────────────────────────────────────────────
#  POPUPS DE CARREGAMENTO E SERVIDOR (Telas iniciais)
# ─────────────────────────────────────────────────────────────────────────────
$loadingXaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Carregando Frota" Height="400" Width="560"
        WindowStartupLocation="CenterScreen" WindowStyle="None" AllowsTransparency="True" Background="Transparent" ResizeMode="NoResize" ShowInTaskbar="False"
        Topmost="False">
    
    <Border Background="#121214" CornerRadius="12" BorderBrush="#27272A" BorderThickness="1.5">
        <Grid Margin="28,24,28,24">
            <Grid.RowDefinitions>
                <RowDefinition Height="Auto"/>
                <RowDefinition Height="Auto"/>
                <RowDefinition Height="Auto"/>
                <RowDefinition Height="*"/>
            </Grid.RowDefinitions>

            <Grid Grid.Row="0" Margin="0,0,0,16">
                <StackPanel>
                    <StackPanel Orientation="Horizontal" VerticalAlignment="Center">
                        <Ellipse Width="7" Height="7" Fill="#219AF9" Margin="0,1,8,0" VerticalAlignment="Center"/>
                        <TextBlock Text="MÓDULO DE SINCRO" Foreground="#219AF9" FontSize="10" FontWeight="Bold"/>
                    </StackPanel>
                    <TextBlock Text="Mapeando infraestrutura de hardware..." Foreground="#71717A" FontSize="12" Margin="0,4,0,0"/>
                </StackPanel>
            </Grid>

            <ProgressBar Grid.Row="1" IsIndeterminate="True" Height="2" Background="#1F1F23" Foreground="#219AF9" BorderThickness="0" Margin="0,0,0,22"/>

            <StackPanel Grid.Row="2" Margin="0,0,0,16">
                <Grid Margin="0,0,0,8">
                    <TextBlock x:Name="TxtStatusLoading" Text="Inicializando rotinas..." Foreground="#E4E4E7" FontSize="12" FontWeight="SemiBold"/>
                    <TextBlock x:Name="TxtPorcentagem" Text="0%" Foreground="#219AF9" FontSize="13" FontWeight="Bold" HorizontalAlignment="Right"/>
                </Grid>
                <ProgressBar x:Name="LoadingBar" Height="6" Minimum="0" Maximum="100" Value="0" Background="#1F1F23" Foreground="#219AF9" BorderThickness="0">
                    <ProgressBar.Resources>
                        <Style TargetType="Border"><Setter Property="CornerRadius" Value="3"/></Style>
                    </ProgressBar.Resources>
                </ProgressBar>
            </StackPanel>

            <Border Grid.Row="3" Background="#070708" CornerRadius="8" Padding="14,12" BorderBrush="#1F1F23" BorderThickness="1">
                <ScrollViewer x:Name="LogScroll" VerticalScrollBarVisibility="Hidden">
                    <TextBlock x:Name="TxtLoadingLog" Text="[SISTEMA] Aguardando diretivas core..." Foreground="#A1A1AA" FontSize="11" FontFamily="Consolas" TextWrapping="Wrap" LineHeight="16"/>
                </ScrollViewer>
            </Border>
        </Grid>
    </Border>
</Window>
"@

$servidorPopupXaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Conectar ao Servidor"
        Height="490" Width="440"
        WindowStartupLocation="CenterScreen"
        WindowStyle="None" AllowsTransparency="True"
        ResizeMode="NoResize"
        ShowInTaskbar="False"
        Background="Transparent">
    <Border Background="#18181B" CornerRadius="14" BorderBrush="#2E2E33" BorderThickness="1" Margin="18">
        <Border.Effect>
            <DropShadowEffect Color="#000000" BlurRadius="28" ShadowDepth="6" Opacity="0.45"/>
        </Border.Effect>

        <Grid Margin="26,24,26,22">
            <Grid.RowDefinitions>
                <RowDefinition Height="Auto"/>
                <RowDefinition Height="Auto"/>
                <RowDefinition Height="Auto"/>
                <RowDefinition Height="*"/>
                <RowDefinition Height="Auto"/>
            </Grid.RowDefinitions>

            <StackPanel x:Name="PnlCabecalho" Grid.Row="0" Margin="0,0,0,16" Cursor="SizeAll">
                <Grid>
                    <Grid.ColumnDefinitions>
                        <ColumnDefinition Width="*"/>
                        <ColumnDefinition Width="Auto"/>
                    </Grid.ColumnDefinitions>
                    <TextBlock Grid.Column="0" Text="Servidor de Impressão" Foreground="#FFFFFF" FontSize="19" FontWeight="Bold"/>
                    <Button x:Name="BtnFecharX" Grid.Column="1" Content="✕" Width="28" Height="28" VerticalAlignment="Top"
                            Foreground="#8B8B93" Background="Transparent" BorderThickness="0" FontSize="13" Cursor="Hand">
                        <Button.Style>
                            <Style TargetType="Button">
                                <Setter Property="Template">
                                    <Setter.Value>
                                        <ControlTemplate TargetType="Button">
                                            <Border Background="{TemplateBinding Background}" CornerRadius="14">
                                                <ContentPresenter HorizontalAlignment="Center" VerticalAlignment="Center"/>
                                            </Border>
                                        </ControlTemplate>
                                    </Setter.Value>
                                </Setter>
                                <Style.Triggers>
                                    <Trigger Property="IsMouseOver" Value="True">
                                        <Setter Property="Background" Value="#2A2A2E"/>
                                        <Setter Property="Foreground" Value="#FFFFFF"/>
                                    </Trigger>
                                </Style.Triggers>
                            </Style>
                        </Button.Style>
                    </Button>
                </Grid>
                <Border Height="1" Background="#26262B" Margin="0,18,0,0"/>
            </StackPanel>

            <StackPanel Grid.Row="1" Margin="0,0,0,16">
                <Image x:Name="LogoServidor" Height="100" Stretch="Uniform" Margin="0,0,0,12" HorizontalAlignment="Center"/>
                <TextBlock Text="Informe o nome ou IP do servidor que deseja consultar." Foreground="#8B8B93" FontSize="12.5" TextWrapping="Wrap" TextAlignment="Center"/>
            </StackPanel>

            <StackPanel Grid.Row="2">
                <Border Background="#212124" CornerRadius="10" Padding="16" BorderBrush="#2E2E33" BorderThickness="1">
                    <StackPanel>
                        <TextBlock Text="SERVIDOR" Foreground="#8B8B93" FontSize="10.5" FontWeight="Bold" Margin="0,0,0,10"/>
                        <Border BorderBrush="#219AF9" BorderThickness="1" CornerRadius="8" Background="#18181B">
                            <TextBox x:Name="TxtServidor"
                                     Background="Transparent" Foreground="#FFFFFF"
                                     BorderThickness="0"
                                     Padding="12,10" FontSize="13.5" CaretBrush="White"
                                     Height="42" VerticalContentAlignment="Center"/>
                        </Border>
                        <TextBlock x:Name="TxtErro" Foreground="#F75C5C" FontSize="11.5"
                                   Margin="0,8,0,0" Visibility="Collapsed"
                                   Text="Por favor, informe o nome do servidor."/>
                    </StackPanel>
                </Border>
            </StackPanel>

            <StackPanel Grid.Row="4" Orientation="Horizontal" HorizontalAlignment="Right" Margin="0,20,0,0">
                <Button x:Name="BtnCancelar" Content="Cancelar" Width="94" Height="38" Margin="0,0,10,0"
                        Foreground="#FFFFFF" FontWeight="SemiBold" BorderThickness="0" Cursor="Hand">
                    <Button.Resources>
                        <Style TargetType="Border"><Setter Property="CornerRadius" Value="8"/></Style>
                    </Button.Resources>
                    <Button.Style>
                        <Style TargetType="Button">
                            <Setter Property="Background" Value="#2E2E33"/>
                            <Style.Triggers>
                                <Trigger Property="IsMouseOver" Value="True">
                                    <Setter Property="Background" Value="#3A3A40"/>
                                </Trigger>
                            </Style.Triggers>
                        </Style>
                    </Button.Style>
                </Button>
                <Button x:Name="BtnConectar" Content="Conectar" Width="130" Height="38"
                        Foreground="#18181B" FontWeight="Bold" BorderThickness="0" Cursor="Hand">
                    <Button.Resources>
                        <Style TargetType="Border"><Setter Property="CornerRadius" Value="8"/></Style>
                    </Button.Resources>
                    <Button.Style>
                        <Style TargetType="Button">
                            <Setter Property="Background" Value="#219AF9"/>
                            <Style.Triggers>
                                <Trigger Property="IsMouseOver" Value="True">
                                    <Setter Property="Background" Value="#4FB2FB"/>
                                </Trigger>
                            </Style.Triggers>
                        </Style>
                    </Button.Style>
                </Button>
            </StackPanel>
        </Grid>
    </Border>
</Window>
"@

function Show-ServidorPopup {
    Write-SystemLog "Abrindo caixa de diálogo de seleção de servidor..." -Level Info
    $servidorPopup = [Windows.Markup.XamlReader]::Load(
        [System.Xml.XmlReader]::Create([System.IO.StringReader]::new($servidorPopupXaml))
    )
    if ($window -and $window.IsVisible) { $servidorPopup.Owner = $window }

    $logoPopup = $servidorPopup.FindName("LogoServidor")
    if ($logoPopup) {
        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            $urlDaLogo = "https://i.ibb.co/XfXbR88H/Logo.png"
            $webClient = New-Object System.Net.WebClient
            $imageBytes = $webClient.DownloadData($urlDaLogo)
            
            $ms = New-Object System.IO.MemoryStream($imageBytes, 0, $imageBytes.Length)
            $bitmap = New-Object System.Windows.Media.Imaging.BitmapImage
            $bitmap.BeginInit()
            $bitmap.StreamSource = $ms
            $bitmap.CacheOption = [System.Windows.Media.Imaging.BitmapCacheOption]::OnLoad
            $bitmap.EndInit()
            $bitmap.Freeze()
            
            $logoPopup.Source = $bitmap
        } catch {
            Write-SystemLog "Falha ao baixar/carregar a logo do popup: $($_.Exception.Message)" -Level Warning
        }
    }

    $txtServidor = $servidorPopup.FindName("TxtServidor")
    $btnConectar = $servidorPopup.FindName("BtnConectar")
    $btnCancelar = $servidorPopup.FindName("BtnCancelar")
    $txtErro     = $servidorPopup.FindName("TxtErro")

    $txtServidor.Text = $script:Config.ServidorPrint
    $servidorPopup.Add_Loaded({ $txtServidor.Focus() | Out-Null; $txtServidor.SelectAll() })

    $txtServidor.Add_KeyDown({
        if ($_.Key -eq [System.Windows.Input.Key]::Return) { $btnConectar.RaiseEvent([System.Windows.RoutedEventArgs]::new([System.Windows.Controls.Primitives.ButtonBase]::ClickEvent)) }
    })

    $btnCancelar.Add_Click({ $servidorPopup.Close() })
    $servidorPopup.FindName("BtnFecharX").Add_Click({ $servidorPopup.Close() })
    $servidorPopup.FindName("PnlCabecalho").Add_MouseLeftButtonDown({ $servidorPopup.DragMove() })

    $btnConectar.Add_Click({
        $valor = $txtServidor.Text.Trim()
        if ([string]::IsNullOrWhiteSpace($valor)) {
            $txtErro.Visibility = [System.Windows.Visibility]::Visible
            $txtServidor.Focus() | Out-Null
            return
        }
        $script:Config.ServidorPrint = $valor
        $servidorPopup.DialogResult = $true
        $servidorPopup.Close()
    })

    return $servidorPopup.ShowDialog()
}

$resultado = Show-ServidorPopup
if ($resultado -ne $true) { 
    Write-SystemLog "Execução encerrada pelo usuário no popup de servidor." -Level Error
    exit 
}

# ─────────────────────────────────────────────────────────────────────────────
#  INICIALIZAÇÃO DO UI PRINCIPAL (DASHBOARD)
# ─────────────────────────────────────────────────────────────────────────────
Write-SystemLog "Carregando e renderizando o Dashboard.xaml..." -Level Info
$xmlReader = [System.Xml.XmlReader]::Create([System.IO.StringReader]::new($script:dashboardXaml))
$window    = [Windows.Markup.XamlReader]::Load($xmlReader)

if ($null -eq $window) {
    Write-SystemLog "A janela 'Dashboard' não pôde ser inicializada." -Level Error
    Write-SystemLog "Pressione qualquer tecla para continuar..." -Level Warning
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

if ($null -ne [System.Windows.Application]::Current) {
    [System.Windows.Application]::Current.ShutdownMode = [System.Windows.ShutdownMode]::OnExplicitShutdown
}

$TabelaImpressoras  = $window.FindName("TabelaImpressoras")
$txtPesquisa        = $window.FindName("TxtPesquisa")
$btnEscanear        = $window.FindName("BtnEscanear")
$lblTotal           = $window.FindName("Total")
$lblOnline          = $window.FindName("Online")
$lblOffline         = $window.FindName("Offline")
$lblAtualizacao     = $window.FindName("UltimaAtualizacao")
$btnFiltroTodos     = $window.FindName("BtnFiltroTodos")
$btnFiltroOnline    = $window.FindName("BtnFiltroOnline")
$btnFiltroOffline   = $window.FindName("BtnFiltroOffline")
$btnTipoTodos       = $window.FindName("BtnTipoTodos")
$btnTipoA4          = $window.FindName("BtnTipoA4")
$btnTipoEtiqueta    = $window.FindName("BtnTipoEtiqueta")
$btnTipoPortatil    = $window.FindName("BtnTipoPortatil")
$RelogioTopo        = $window.FindName("RelogioTopo")
$TxtStatusServico   = $window.FindName("TxtStatusServico")
$BtnExportar        = $window.FindName("BtnExportar")
$BtnSino            = $window.FindName("BtnSino")
$BtnTrocarServidor  = $window.FindName("BtnTrocarServidor")

$script:LinhasRegistradas = [System.Collections.Generic.HashSet[string]]::new()
$script:FiltroStatus = "Todos"
$script:FiltroTipo = "Todos"

$clockTimer = New-Object System.Windows.Threading.DispatcherTimer
$clockTimer.Interval = [TimeSpan]::FromSeconds(1)
$clockTimer.Add_Tick({ $RelogioTopo.Text = (Get-Date).ToString("dd/MM/yyyy HH:mm:ss") })
$clockTimer.Start()

$BtnTrocarServidor.Add_Click({
    Write-SystemLog "Botão 'Trocar Servidor' acionado." -Level Info
    $res = Show-ServidorPopup
    if ($res -eq $true) {
        Write-SystemLog "Novo servidor configurado: '$($script:Config.ServidorPrint)'. Disparando recarregamento..." -Level Success
        Atualizar-ImpressorasAsync
    }
})

$BtnExportar.Add_Click({
    try {
        if ($null -eq $script:impressoras -or $script:impressoras.Count -eq 0) {
            [System.Windows.MessageBox]::Show("Sem dados para exportar. Faça um scan primeiro.", "Aviso", 0, 48)
            return
        }
        
        $sfd = New-Object Microsoft.Win32.SaveFileDialog
        $sfd.Filter = "Arquivos CSV (*.csv)|*.csv"
        $sfd.FileName = "Frota_Impressoras.csv"
        if ($sfd.ShowDialog() -ne $true) { return }
        
        $caminho = $sfd.FileName
        
        $dadosLimpos = $script:impressoras | ForEach-Object {
            $tonerMsg = if ($null -ne $_.ListaToners -and $_.ListaToners.Count -gt 0) { 
                ($_.ListaToners | ForEach-Object { $_.Valor }) -join " | "
            } else { "N/A" }
            [PSCustomObject]@{
                Nome   = $_.Nome
                IP     = $_.IP
                Modelo = $_.Modelo
                Status = $_.Status
                Toner  = $tonerMsg
                Uptime = $_.Uptime
            }
        }
        
        $dadosLimpos | Export-Csv -LiteralPath $caminho -NoTypeInformation -Encoding UTF8 -Delimiter ";"
        [System.Windows.MessageBox]::Show("Relatório CSV gerado com sucesso!", "Concluído", 0, 64)
    } catch {
        [System.Windows.MessageBox]::Show("Falha ao exportar: $_", "Erro", 0, 16)
    }
})

$BtnSino.Add_Click({
    $offline = ($script:impressoras | Where-Object { $_.Status -eq "Offline" }).Count
    $msg     = if ($offline -eq 0) { "Nenhuma impressora offline." } else { "$offline impressora(s) offline detectada(s)." }
    $corMsg  = if ($offline -eq 0) { "#219AF9" } else { "#F75C5C" }

    $sinoXaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Notificações" Height="240" Width="330"
        WindowStartupLocation="CenterScreen" WindowStyle="None" AllowsTransparency="True"
        Background="Transparent" ResizeMode="NoResize" ShowInTaskbar="False">
    <Border Background="#18181B" CornerRadius="14" BorderBrush="#2E2E33" BorderThickness="1" Margin="18">
        <Border.Effect>
            <DropShadowEffect Color="#000000" BlurRadius="28" ShadowDepth="6" Opacity="0.45"/>
        </Border.Effect>
        <Grid Margin="22,20,22,18">
            <Grid.RowDefinitions>
                <RowDefinition Height="Auto"/>
                <RowDefinition Height="*"/>
                <RowDefinition Height="Auto"/>
            </Grid.RowDefinitions>

            <StackPanel x:Name="PnlCabecalho" Grid.Row="0" Margin="0,0,0,14" Cursor="SizeAll">
                <Grid>
                    <Grid.ColumnDefinitions>
                        <ColumnDefinition Width="*"/>
                        <ColumnDefinition Width="Auto"/>
                    </Grid.ColumnDefinitions>
                    <TextBlock Grid.Column="0" Text="Alertas do Sistema" Foreground="#FFFFFF" FontSize="17" FontWeight="Bold"/>
                    <Button x:Name="BtnFecharX" Grid.Column="1" Content="✕" Width="26" Height="26" VerticalAlignment="Top"
                            Foreground="#8B8B93" Background="Transparent" BorderThickness="0" FontSize="12" Cursor="Hand">
                        <Button.Style>
                            <Style TargetType="Button">
                                <Setter Property="Template">
                                    <Setter.Value>
                                        <ControlTemplate TargetType="Button">
                                            <Border Background="{TemplateBinding Background}" CornerRadius="13">
                                                <ContentPresenter HorizontalAlignment="Center" VerticalAlignment="Center"/>
                                            </Border>
                                        </ControlTemplate>
                                    </Setter.Value>
                                </Setter>
                                <Style.Triggers>
                                    <Trigger Property="IsMouseOver" Value="True">
                                        <Setter Property="Background" Value="#2A2A2E"/>
                                        <Setter Property="Foreground" Value="#FFFFFF"/>
                                    </Trigger>
                                </Style.Triggers>
                            </Style>
                        </Button.Style>
                    </Button>
                </Grid>
                <Border Height="1" Background="#26262B" Margin="0,14,0,0"/>
            </StackPanel>

            <Border Grid.Row="1" Background="#212124" CornerRadius="10" Padding="16"
                    BorderBrush="#2E2E33" BorderThickness="1">
                <TextBlock x:Name="TxtMensagem" Foreground="#D4D4D8" TextWrapping="Wrap" FontSize="13" LineHeight="19"/>
            </Border>

            <Button x:Name="BtnOk" Grid.Row="2" Content="OK" Width="90" Height="36"
                    HorizontalAlignment="Right" Margin="0,16,0,0"
                    Foreground="#FFFFFF" FontWeight="SemiBold" BorderThickness="0" Cursor="Hand">
                <Button.Resources>
                    <Style TargetType="Border"><Setter Property="CornerRadius" Value="8"/></Style>
                </Button.Resources>
                <Button.Style>
                    <Style TargetType="Button">
                        <Setter Property="Background" Value="#219AF9"/>
                        <Style.Triggers>
                            <Trigger Property="IsMouseOver" Value="True">
                                <Setter Property="Background" Value="#1880d8"/>
                            </Trigger>
                        </Style.Triggers>
                    </Style>
                </Button.Style>
            </Button>
        </Grid>
    </Border>
</Window>
"@
    $sinoPopup  = [Windows.Markup.XamlReader]::Load([System.Xml.XmlReader]::Create([System.IO.StringReader]::new($sinoXaml)))
    if ($window -and $window.IsVisible) { $sinoPopup.Owner = $window }
    $txtMsg     = $sinoPopup.FindName("TxtMensagem")
    $btnOk      = $sinoPopup.FindName("BtnOk")

    $txtMsg.Text       = $msg
    $txtMsg.Foreground = [System.Windows.Media.BrushConverter]::new().ConvertFromString($corMsg)

    $btnOk.Add_Click({ $sinoPopup.Close() })
    $sinoPopup.FindName("BtnFecharX").Add_Click({ $sinoPopup.Close() })
    $sinoPopup.FindName("PnlCabecalho").Add_MouseLeftButtonDown({ $sinoPopup.DragMove() })
    $sinoPopup.ShowDialog() | Out-Null
})

$logoImage = $window.FindName("LogoElgin")
if ($logoImage) {
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $urlDaLogo = "https://logodownload.org/wp-content/uploads/2016/09/elgin-logo-0-1-1536x1536.png"
        $webClient = New-Object System.Net.WebClient
        $imageBytes = $webClient.DownloadData($urlDaLogo)
        $ms = New-Object System.IO.MemoryStream($imageBytes, 0, $imageBytes.Length)
        $bitmap = New-Object System.Windows.Media.Imaging.BitmapImage
        $bitmap.BeginInit()
        $bitmap.StreamSource = $ms
        $bitmap.CacheOption = [System.Windows.Media.Imaging.BitmapCacheOption]::OnLoad
        $bitmap.EndInit()
        $bitmap.Freeze()
        
        $logoImage.Source = $bitmap
        try {
            $iconeUri = New-Object System.Uri("https://www.elgin.com.br/favicon.ico", [System.UriKind]::Absolute)
            $window.Icon = [System.Windows.Media.Imaging.BitmapFrame]::Create($iconeUri)
        } catch { }
    } catch {
        Write-SystemLog "Falha ao baixar/carregar a logo da URL: $($_.Exception.Message)" -Level Warning
    }
}

$TabelaImpressoras.AddHandler([System.Windows.Controls.Primitives.ButtonBase]::ClickEvent, [System.Windows.RoutedEventHandler]{
    param($sender, $e)
    
    $btn = $e.OriginalSource
    if ($btn -isnot [System.Windows.Controls.Button]) { return }

    $dc = $btn.DataContext
    if ($null -eq $dc -or [string]::IsNullOrWhiteSpace($dc.IP)) { return }

    switch ($btn.Name) {
        "BtnExpandirGrupo" {
            Toggle-GrupoIP -IP $dc.IP
        }
        "BtnAbrirCard" {
            try {
                $cardPopup = [Windows.Markup.XamlReader]::Load([System.Xml.XmlReader]::Create([System.IO.StringReader]::new($script:cardDetalhesXaml)))
                if ($window -and $window.IsVisible) { $cardPopup.Owner = $window }
                
                $cardPopup.FindName("TxtNome").Text   = $dc.Nome
                $cardPopup.FindName("TxtModelo").Text = $dc.Modelo
                $cardPopup.FindName("TxtIP").Text     = $dc.IP
                $cardPopup.FindName("TxtStatus").Text = $dc.Status
                $cardPopup.FindName("TxtUptime").Text = $dc.Uptime
                $cardPopup.FindName("TxtPaginas").Text = $dc.PageCount
                
                $tonerContainer = $cardPopup.FindName("TonerContainer")
                if ($null -ne $tonerContainer) { $tonerContainer.ItemsSource = $dc.ListaToners }

                # Lógica do disparo de webhook manual através do card
                $btnAlertaToner = $cardPopup.FindName("BtnAlertaToner")
                if ($null -ne $btnAlertaToner) {
                    $btnAlertaToner.Add_Click({
                        $menorPct = 100
                        $corMenor = "Não identificado"

                        foreach ($t in $dc.ListaToners) {
                            if ($t.Valor -match '(?:([CMYK]):)?(\d+)%') {
                                $val = [int]$Matches[2]
                                if ($val -le $menorPct) {
                                    $menorPct = $val
                                    $sigla = $Matches[1]
                                    $corMenor = switch ($sigla) { 'C'{"Ciano"} 'M'{"Magenta"} 'Y'{"Amarelo"} 'K'{"Preto"} default{"Preto"} }
                                }
                            }
                        }

                        if ($menorPct -eq 100) {
                            Show-ToastNotification -Mensagem "Nenhum toner rastreável nesta impressora." -Tipo "Erro" -JanelaPai $cardPopup
                            return
                        }

                        $sucesso = Send-AlertaWebhook -Impressora $dc.Nome -Modelo $dc.Modelo -Cor $corMenor -Nivel "$menorPct%" -Manual $true
                        if ($sucesso) {
                            Show-ToastNotification -Mensagem "Alerta disparado para o Teams!" -Tipo "Sucesso" -JanelaPai $cardPopup
                        } else {
                            Show-ToastNotification -Mensagem "Falha de conexão. Consulte os logs." -Tipo "Erro" -JanelaPai $cardPopup
                        }
                    })
                }

                $cardPopup.FindName("BtnFecharCard").Add_Click({ $cardPopup.Close() })
                $cardPopup.FindName("BtnFecharX").Add_Click({ $cardPopup.Close() })
                $cardPopup.FindName("PnlCabecalho").Add_MouseLeftButtonDown({ $cardPopup.DragMove() })
                $cardPopup.ShowDialog() | Out-Null
            } catch { [System.Windows.MessageBox]::Show("Erro ao carregar Card: $_", "Erro Interno") }
        }
        "BtnAbrirSite" {
            if (-not [string]::IsNullOrWhiteSpace($dc.IP)) { Start-Process "http://$($dc.IP)" }
        }
        "BtnImprimirTeste" {
            try {
                $impressora = Get-Printer -ErrorAction Stop | Where-Object { $_.Name -eq $dc.Nome } | Select-Object -First 1
                if ($impressora) {
                    rundll32 printui.dll,PrintUIEntry /k /n "$($impressora.Name)"
                } else {
                    [System.Windows.MessageBox]::Show("Essa impressora não está instalada no seu computador local.", "Aviso", 0, 48)
                }
            } catch { [System.Windows.MessageBox]::Show("Falha ao disparar teste.", "Erro", 0, 16) }
        }
        "BtnDriver" {
            Show-DriverPopup -nomeImpressora $dc.Nome -modeloImpressora $dc.Modelo -ipImpressora $dc.IP
        }
    }
})

function Set-FiltroAtivo {
    param([string]$filtro)
    $script:FiltroStatus = $filtro

    $btnFiltroTodos.Background   = if ($filtro -eq "Todos")   { "#2A2A2A" } else { "Transparent" }
    $btnFiltroOnline.Background  = if ($filtro -eq "Online")  { "#2A2A2A" } else { "Transparent" }
    $btnFiltroOffline.Background = if ($filtro -eq "Offline") { "#2A2A2A" } else { "Transparent" }

    $btnFiltroTodos.Foreground   = if ($filtro -eq "Todos")   { "White" } else { "#9CA3AF" }
    $btnFiltroOnline.Foreground  = if ($filtro -eq "Online")  { "White" } else { "#9CA3AF" }
    $btnFiltroOffline.Foreground = if ($filtro -eq "Offline") { "White" } else { "#9CA3AF" }

    $btnFiltroTodos.Tag   = if ($filtro -eq "Todos")   { "3,0,0,0" } else { "0" }
    $btnFiltroOnline.Tag  = if ($filtro -eq "Online")  { "3,0,0,0" } else { "0" }
    $btnFiltroOffline.Tag = if ($filtro -eq "Offline") { "3,0,0,0" } else { "0" }

    Invoke-FiltroTabela
}

function Set-FiltroTipoAtivo {
    param([string]$filtro)
    $script:FiltroTipo = $filtro

    $mapaBotoes = @{ Todos=$btnTipoTodos; A4=$btnTipoA4; Etiqueta=$btnTipoEtiqueta; Portatil=$btnTipoPortatil }
    foreach ($chave in $mapaBotoes.Keys) {
        $ativo = ($filtro -eq $chave)
        $mapaBotoes[$chave].Background = if ($ativo) { "#2A2A2A" } else { "Transparent" }
        $mapaBotoes[$chave].Foreground = if ($ativo) { "White" } else { "#9CA3AF" }
        $mapaBotoes[$chave].Tag        = if ($ativo) { "3,0,0,0" } else { "0" }
    }

    Invoke-FiltroTabela
}

function Invoke-FiltroTabela {
    $texto = $txtPesquisa.Text.Trim()
    if ($texto -eq "Pesquisar impressora...") { $texto = "" }

    $resultado = $script:impressoras | Where-Object {
        ($script:FiltroStatus -eq "Todos" -or $_.Status -eq $script:FiltroStatus) -and
        ($script:FiltroTipo -eq "Todos" -or (Obter-TipoImpressora -Nome $_.Nome -Modelo $_.Modelo) -eq $script:FiltroTipo) -and
        ($texto -eq "" -or $_.Nome -match [regex]::Escape($texto) -or $_.IP -match [regex]::Escape($texto) -or $_.Modelo -match [regex]::Escape($texto))
    }
    Import-Tabela @($resultado)
}

function Set-Contadores {
    param($lista)
    $lblTotal.Text       = $script:impressoras.Count
    $lblOnline.Text      = ($script:impressoras | Where-Object { $_.Status -eq "Online" }).Count
    $lblOffline.Text     = ($script:impressoras | Where-Object { $_.Status -eq "Offline" }).Count
    $lblAtualizacao.Text = (Get-Date).ToString("dd/MM/yyyy HH:mm:ss")
}

$script:GruposExpandidos = @{}
$script:UltimaListaBase = @()

function Build-ListaExibicaoAgrupada {
    param($lista)

    $exibicao = [System.Collections.Generic.List[object]]::new()
    if ($null -eq $lista -or @($lista).Count -eq 0) { return $exibicao }

    $gruposPorIP = @($lista) | Group-Object -Property IP

    foreach ($grupo in $gruposPorIP) {
        if ($grupo.Count -le 1 -or [string]::IsNullOrWhiteSpace($grupo.Name)) {
            foreach ($item in $grupo.Group) {
                $item | Add-Member -NotePropertyName EhPrincipalGrupo -NotePropertyValue $false -Force
                $item | Add-Member -NotePropertyName IsChildRow        -NotePropertyValue $false -Force
                $item | Add-Member -NotePropertyName QtdGrupo          -NotePropertyValue 1 -Force
                $item | Add-Member -NotePropertyName Expandido         -NotePropertyValue $false -Force
                $item | Add-Member -NotePropertyName ExpansorVis       -NotePropertyValue ([System.Windows.Visibility]::Collapsed) -Force
                $item | Add-Member -NotePropertyName IndentMargin      -NotePropertyValue ([System.Windows.Thickness]::new(0)) -Force
                $exibicao.Add($item) | Out-Null
            }
            continue
        }

        $ip = $grupo.Name
        $membros = $grupo.Group | Sort-Object { if ($_.Status -eq 'Online') { 0 } else { 1 } }
        $expandido = if ($script:GruposExpandidos.ContainsKey($ip)) { $script:GruposExpandidos[$ip] } else { $false }

        $principal = $membros | Select-Object -First 1
        $principal | Add-Member -NotePropertyName EhPrincipalGrupo -NotePropertyValue $true -Force
        $principal | Add-Member -NotePropertyName IsChildRow        -NotePropertyValue $false -Force
        $principal | Add-Member -NotePropertyName QtdGrupo          -NotePropertyValue $membros.Count -Force
        $principal | Add-Member -NotePropertyName Expandido         -NotePropertyValue $expandido -Force
        $principal | Add-Member -NotePropertyName ExpansorVis       -NotePropertyValue ([System.Windows.Visibility]::Visible) -Force
        $principal | Add-Member -NotePropertyName IndentMargin      -NotePropertyValue ([System.Windows.Thickness]::new(0)) -Force
        $exibicao.Add($principal) | Out-Null

        if ($expandido) {
            foreach ($filho in ($membros | Select-Object -Skip 1)) {
                $filho | Add-Member -NotePropertyName EhPrincipalGrupo -NotePropertyValue $false -Force
                $filho | Add-Member -NotePropertyName IsChildRow        -NotePropertyValue $true -Force
                $filho | Add-Member -NotePropertyName QtdGrupo          -NotePropertyValue $membros.Count -Force
                $filho | Add-Member -NotePropertyName Expandido         -NotePropertyValue $false -Force
                $filho | Add-Member -NotePropertyName ExpansorVis       -NotePropertyValue ([System.Windows.Visibility]::Collapsed) -Force
                $filho | Add-Member -NotePropertyName IndentMargin      -NotePropertyValue ([System.Windows.Thickness]::new(20,0,0,0)) -Force
                $exibicao.Add($filho) | Out-Null
            }
        }
    }

    return $exibicao
}

function Toggle-GrupoIP {
    param([string]$IP)
    if ([string]::IsNullOrWhiteSpace($IP)) { return }
    $atual = if ($script:GruposExpandidos.ContainsKey($IP)) { $script:GruposExpandidos[$IP] } else { $false }
    $script:GruposExpandidos[$IP] = -not $atual
    Import-Tabela $script:UltimaListaBase
}

function Import-Tabela {
    param($lista)
    $script:LinhasRegistradas.Clear()
    $script:UltimaListaBase = $lista

    $listaAgrupada = Build-ListaExibicaoAgrupada -lista $lista

    $col = [System.Collections.ObjectModel.ObservableCollection[object]]::new()
    foreach ($item in $listaAgrupada) { $col.Add($item) }
    $TabelaImpressoras.ItemsSource = $col
    Set-Contadores $lista
}

function Atualizar-ImpressorasAsync {
    param([bool]$Silencioso = $false)

    if ($script:IsScanning) {
        Write-SystemLog "Scan já em andamento, ignorando chamada duplicada." -Level Warning
        return
    }
    $script:IsScanning = $true

    Write-SystemLog ">>> Iniciando ciclo de varredura completo da frota <<<" -Level Success
    $btnEscanear.IsEnabled = $false
    if (-not $Silencioso) { $btnEscanear.Content = "Escaneando..." }
    $TxtStatusServico.Text = "Varrendo rede..."
    $filtroAtual = $script:FiltroStatus

    if (-not $Silencioso) {
        $loadingWindow = [Windows.Markup.XamlReader]::Load([System.Xml.XmlReader]::Create([System.IO.StringReader]::new($loadingXaml)))
        $loadingWindow.Add_MouseLeftButtonDown({ $this.DragMove() })
        
        $script:loadingBar       = $loadingWindow.FindName("LoadingBar")
        $script:txtPorcentagem   = $loadingWindow.FindName("TxtPorcentagem")
        $script:txtStatusLoading = $loadingWindow.FindName("TxtStatusLoading")
        $script:txtLoadingLog    = $loadingWindow.FindName("TxtLoadingLog")
        $script:logScroll        = $loadingWindow.FindName("LogScroll")

        if ($window.IsVisible) { $loadingWindow.Owner = $window }
        $script:txtStatusLoading.Text = "Conectando a: $($script:Config.ServidorPrint)"
        $loadingWindow.Show()
    } else {
        $script:loadingBar = $null; $script:txtPorcentagem = $null; $script:txtStatusLoading = $null; $script:txtLoadingLog = $null
    }

    [System.Windows.Threading.Dispatcher]::CurrentDispatcher.Invoke([System.Action]{}, [System.Windows.Threading.DispatcherPriority]::Render)

    try {
        $resultado = Get-ImpressorasEmpresa
        $script:impressoras = $resultado

        # --- INÍCIO DA VALIDAÇÃO AUTOMÁTICA DE TONER (< 5%) ---
        if ($null -eq $script:TonerHistorico) { $script:TonerHistorico = @{} }

        foreach ($imp in $script:impressoras) {
            if ($imp.Status -eq 'Online' -and $imp.ListaToners) {
                foreach ($t in $imp.ListaToners) {
                    if ($t.Valor -match '(?:([CMYK]):)?(\d+)%') {
                        $pct = [int]$Matches[2]
                        $sigla = $Matches[1]
                        $corNome = switch ($sigla) { 'C'{"Ciano"} 'M'{"Magenta"} 'Y'{"Amarelo"} 'K'{"Preto"} default{"Preto"} }
                        
                        $chave = "$($imp.Nome)-$corNome"
                        
                        if ($pct -le 5) {
                            if (-not $script:TonerHistorico.ContainsKey($chave) -or $pct -lt $script:TonerHistorico[$chave]) {
                                Send-AlertaWebhook -Impressora $imp.Nome -Modelo $imp.Modelo -ListaToners @([PSCustomObject]@{Cor=$corNome; Nivel="$pct%"}) -Manual $false
                            }
                        }
                        $script:TonerHistorico[$chave] = $pct
                    }
                }
            }
        }
        # --- FIM DA VALIDAÇÃO AUTOMÁTICA ---
        
        Write-SystemLog "Injetando novos dados na tabela visual WPF..." -Level Info
        Import-Tabela $script:impressoras
        Set-FiltroAtivo $filtroAtual
    }
    catch {
        Write-SystemLog "Falha geral ao carregar dados visuais: $($_.Exception.Message)" -Level Error
        [System.Windows.MessageBox]::Show("Erro ao atualizar dados da frota: $($_.Exception.Message)", "Erro de Varredura")
    }
    finally {
        if (-not $Silencioso -and $null -ne $loadingWindow) {
            $loadingWindow.Close()
        }
        
        $btnEscanear.Content   = "Escanear Rede"
        $btnEscanear.IsEnabled = $true
        $TxtStatusServico.Text = "Aguardando..."
        Write-SystemLog "Varredura finalizada. Sistema pronto para uso." -Level Success
        $script:IsScanning = $false
    }
}

function Iniciar-CarregamentoInicial {
    Atualizar-ImpressorasAsync
}

$script:impressoras = @()
$script:IsScanning = $false

$btnFiltroTodos.Add_Click({ Set-FiltroAtivo "Todos" })
$btnFiltroOnline.Add_Click({ Set-FiltroAtivo "Online" })
$btnFiltroOffline.Add_Click({ Set-FiltroAtivo "Offline" })
$btnTipoTodos.Add_Click({ Set-FiltroTipoAtivo "Todos" })
$btnTipoA4.Add_Click({ Set-FiltroTipoAtivo "A4" })
$btnTipoEtiqueta.Add_Click({ Set-FiltroTipoAtivo "Etiqueta" })
$btnTipoPortatil.Add_Click({ Set-FiltroTipoAtivo "Portatil" })

$txtPesquisa.Add_GotFocus({ if ($this.Text -eq "Pesquisar impressora...") { $this.Text = "" } })
$txtPesquisa.Add_LostFocus({ if ([string]::IsNullOrWhiteSpace($this.Text)) { $this.Text = "Pesquisar impressora..." } })
$txtPesquisa.Add_TextChanged({ Invoke-FiltroTabela })

$btnEscanear.Add_Click({ Atualizar-ImpressorasAsync })

$timer = New-Object System.Windows.Threading.DispatcherTimer
$timer.Interval = [TimeSpan]::FromMinutes([int]$script:Config.TempoRefreshMinutos)
$timer.Add_Tick({ 
    Write-SystemLog "Disparando atualização automática programada..." -Level Info
    Atualizar-ImpressorasAsync -Silencioso $true
})

$window.Add_Loaded({
    Write-SystemLog "Janela carregada com sucesso. Iniciando rotinas..." -Level Success
    $timer.Start()
    Iniciar-CarregamentoInicial
})

$window.Add_Closed({
    Write-SystemLog "Encerrando aplicação e finalizando timers." -Level Error
    $timer.Stop()
    try { Stop-Transcript | Out-Null } catch {}
    if ($null -ne [System.Windows.Application]::Current) {
        [System.Windows.Application]::Current.Shutdown()
    }
})

$window.ShowDialog() | Out-Null