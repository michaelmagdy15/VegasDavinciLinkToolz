using System;
using System.Reflection;
using ScriptPortal.Vegas;

class Program
{
    static void Main()
    {
        var fadeProp = typeof(TrackEvent).GetProperty("FadeIn");
        if (fadeProp != null)
        {
            Console.WriteLine("Fade type: " + fadeProp.PropertyType.FullName);
            foreach (var p in fadeProp.PropertyType.GetProperties())
            {
                Console.WriteLine("  " + p.Name + " : " + p.PropertyType.FullName);
            }
        }

        Console.WriteLine("--- AudioEvent ---");
        foreach (var p in typeof(AudioEvent).GetProperties())
        {
            Console.WriteLine(p.Name + " : " + p.PropertyType.FullName);
        }

        Console.WriteLine("--- VideoEvent ---");
        foreach (var p in typeof(VideoEvent).GetProperties())
        {
            Console.WriteLine(p.Name + " : " + p.PropertyType.FullName);
        }
    }
}
