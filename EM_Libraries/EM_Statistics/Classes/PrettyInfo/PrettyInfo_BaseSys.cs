﻿namespace EM_Statistics
{
    public static partial class PrettyInfoProvider
    {
        private class PrettyInfo_BaseSys : PrettyInfo
        {
            protected override string ident { get => PRETTY_INFO_BASE_SYS; }

            internal override string ReplaceText(string origText, PrettyInfoResources resources)
            {
                return origText.Replace(ident, resources.baseSystems[0].GetSystemName());
            }
        }
    }
}
