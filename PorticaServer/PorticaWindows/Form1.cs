using System.IO.Compression;

namespace PorticaWindows
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_FormClosing(object? sender, FormClosingEventArgs e)
        {
            if (p != null)
            {
                if (!p.HasExited)
                {
                    p.Kill();
                }
            }
            if (p2 != null)
            {
                if (!p2.HasExited) p2.Kill();
            }
            if (p3 != null)
            {
                if (!p3.HasExited) p3.Kill();
            }
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            load();
        }

        private async void load()
        {
            String ret, ret2, ret3;
            var zip = "python-3.9.13-embed-amd64.zip";
            var folder = "./";
            ZipFile.ExtractToDirectory(zip, folder, true);
            var sr = new StreamReader("python39._pth");
            var text = sr.ReadToEnd();
            sr.Close();
            text = text.Replace("#import site", "import site");
            var sw = new StreamWriter("python39._pth");
            sw.Write(text);
            sw.Close();
            p = new System.Diagnostics.Process();
            p.StartInfo.FileName = "python.exe";
            p.StartInfo.UseShellExecute = false;
            p.StartInfo.RedirectStandardOutput = true;
            p.StartInfo.RedirectStandardInput = false;
            p.StartInfo.RedirectStandardError = true;
            p.StartInfo.CreateNoWindow = true;
            p.StartInfo.Arguments = "get-pip.py --no-warn-script-location";
            p.Start();
            while (!p.HasExited)
            {
                textBox1.Text += await p.StandardOutput.ReadLineAsync() + "\r\n";
                textBox1.Update();
            }
            if ((ret = p.StandardError.ReadToEnd()) == "") textBox1.Text += "Fin.\r\n";
            else textBox1.Text += ret + "\r\n";
            p2 = new System.Diagnostics.Process();
            p2.StartInfo.FileName = "Scripts/pip.exe";
            p2.StartInfo.UseShellExecute = false;
            p2.StartInfo.RedirectStandardOutput = true;
            p2.StartInfo.RedirectStandardInput = true;
            p2.StartInfo.RedirectStandardError = true;
            p2.StartInfo.CreateNoWindow = true;
            p2.StartInfo.Arguments = "install -r requirements.txt";
            p2.Start();
            while (!p2.HasExited)
            {
                textBox1.Text += await p2.StandardOutput.ReadLineAsync() + "\r\n";
                textBox1.Update();
            }
            if ((ret2 = p2.StandardError.ReadToEnd()) == "") textBox1.Text += "Fin.\r\n";
            else textBox1.Text += ret2 + "\r\n";

            p3 = new System.Diagnostics.Process();
            p3.StartInfo.FileName = "python.exe";
            p3.StartInfo.UseShellExecute = false;
            p3.StartInfo.RedirectStandardOutput = true;
            p3.StartInfo.RedirectStandardInput = false;
            p3.StartInfo.RedirectStandardError = true;
            p3.StartInfo.CreateNoWindow = true;
            p3.StartInfo.Arguments = "manage.py migrate";
            p3.Start();
            while (!p3.HasExited)
            {
                textBox1.Text += await p3.StandardOutput.ReadLineAsync() + "\r\n";
                textBox1.Update();
            }
            if ((ret3 = p3.StandardError.ReadToEnd()) == "") textBox1.Text += "Fin.\r\n";
            else textBox1.Text += ret3 + "\r\n";
            p0 = new System.Diagnostics.Process();
            p0.StartInfo.FileName = "python.exe";
           /* p0.StartInfo.UseShellExecute = false;
            p0.StartInfo.RedirectStandardOutput = true;
            p0.StartInfo.RedirectStandardInput = true;
            p0.StartInfo.RedirectStandardError = true;
            p0.StartInfo.CreateNoWindow = true;*/
            p0.StartInfo.Arguments = "manage.py runserver 5000";
            p0.Start();
            /*while (!p0.HasExited)
            {
                textBox1.Text += await p0.StandardError.ReadLineAsync();
                textBox1.Update();
            }
            textBox1.Text += "Fin.";*/
            if (ret == "" && ret2 == "" && ret3 == "")
            {
                await Task.Delay(3000);
                this.Close();
            }
        }
        System.Diagnostics.Process p0, p, p2, p3;
    }
}