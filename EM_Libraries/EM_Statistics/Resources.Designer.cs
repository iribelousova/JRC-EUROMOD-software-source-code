﻿//------------------------------------------------------------------------------
// <auto-generated>
//     This code was generated by a tool.
//     Runtime Version:4.0.30319.42000
//
//     Changes to this file may cause incorrect behavior and will be lost if
//     the code is regenerated.
// </auto-generated>
//------------------------------------------------------------------------------

namespace EM_Statistics {
    using System;
    
    
    /// <summary>
    ///   A strongly-typed resource class, for looking up localized strings, etc.
    /// </summary>
    // This class was auto-generated by the StronglyTypedResourceBuilder
    // class via a tool like ResGen or Visual Studio.
    // To add or remove a member, edit your .ResX file then rerun ResGen
    // with the /str option, or rebuild your VS project.
    [global::System.CodeDom.Compiler.GeneratedCodeAttribute("System.Resources.Tools.StronglyTypedResourceBuilder", "15.0.0.0")]
    [global::System.Diagnostics.DebuggerNonUserCodeAttribute()]
    [global::System.Runtime.CompilerServices.CompilerGeneratedAttribute()]
    internal class Resources {
        
        private static global::System.Resources.ResourceManager resourceMan;
        
        private static global::System.Globalization.CultureInfo resourceCulture;
        
        [global::System.Diagnostics.CodeAnalysis.SuppressMessageAttribute("Microsoft.Performance", "CA1811:AvoidUncalledPrivateCode")]
        internal Resources() {
        }
        
        /// <summary>
        ///   Returns the cached ResourceManager instance used by this class.
        /// </summary>
        [global::System.ComponentModel.EditorBrowsableAttribute(global::System.ComponentModel.EditorBrowsableState.Advanced)]
        internal static global::System.Resources.ResourceManager ResourceManager {
            get {
                if (object.ReferenceEquals(resourceMan, null)) {
                    global::System.Resources.ResourceManager temp = new global::System.Resources.ResourceManager("EM_Statistics.Resources", typeof(Resources).Assembly);
                    resourceMan = temp;
                }
                return resourceMan;
            }
        }
        
        /// <summary>
        ///   Overrides the current thread's CurrentUICulture property for all
        ///   resource lookups using this strongly typed resource class.
        /// </summary>
        [global::System.ComponentModel.EditorBrowsableAttribute(global::System.ComponentModel.EditorBrowsableState.Advanced)]
        internal static global::System.Globalization.CultureInfo Culture {
            get {
                return resourceCulture;
            }
            set {
                resourceCulture = value;
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to &lt;a id=&quot;emsta-button-id-PLACEHOLDER_PACKAGE_KEY&quot; onclick=&quot;PLACEHOLDER_LINK&quot; class=&quot;w3-bar-item w3-button w3-hover-gray&quot;&gt;PLACEHOLDER_TEXT&lt;/a&gt;
        ///.
        /// </summary>
        internal static string Button_html {
            get {
                return ResourceManager.GetString("Button_html", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to &lt;div id=&quot;TabContent-PLACEHOLDER_PACKAGE_KEY&quot; class=&quot;w3-container w3-cell-middle&quot; style=&quot;height: 100%&quot;&gt;&lt;/div&gt;
        ///.
        /// </summary>
        internal static string Content_html {
            get {
                return ResourceManager.GetString("Content_html", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to // This library fills the statistics UI with results, using the JSON obtained from the EM_LightBackEnd server.
        ///// HTML building blocks
        ///
        ///var CONTAINER_HEAD_ID_PREFIX = &quot;ContainerHead_&quot;;
        ///var CONTAINER_BODY_ID_PREFIX = &quot;ContainerBody_&quot;;
        ///
        ///
        ///// This calls the BackEnd to get the progress update and runs HandleProgress once the response is back
        ///function GetStatsAgain() {
        ///    embe_BackEndRequest(emsta_MakeStatisticsUI, responderKey + &quot;_LoadStatistics&quot;, param);
        ///}
        ///
        ///function GetStatsContent(key)
        ///{
        ///    emb [rest of string was truncated]&quot;;.
        /// </summary>
        internal static string LoadStatistics_js {
            get {
                return ResourceManager.GetString("LoadStatistics_js", resourceCulture);
            }
        }
        
        /// <summary>
        ///   Looks up a localized string similar to &lt;!DOCTYPE html&gt;
        ///&lt;html&gt;
        ///&lt;head&gt;
        ///    &lt;meta http-equiv=&quot;X-UA-Compatible&quot; content=&quot;IE=10&quot; /&gt; &lt;!-- instead of IE4 use version 10 of Internet Explorer, or the installed version, if lower --&gt;
        ///    &lt;meta charset=&quot;UTF-8&quot; /&gt;
        ///    &lt;link rel=&quot;stylesheet&quot; type=&quot;text/css&quot; href=&quot;w3.css&quot;&gt;
        ///    &lt;link rel=&quot;stylesheet&quot; type=&quot;text/css&quot; href=&quot;Chart.min.css&quot;&gt;
        ///    &lt;link rel=&quot;stylesheet&quot; href=&quot;tlite.css&quot; /&gt;
        ///    &lt;!--change w3-css default font-size (15px) and line-spacing(1.5) to use less space--&gt;
        ///    &lt;style&gt;
        ///        html, bod [rest of string was truncated]&quot;;.
        /// </summary>
        internal static string statistics_html {
            get {
                return ResourceManager.GetString("statistics_html", resourceCulture);
            }
        }
    }
}
