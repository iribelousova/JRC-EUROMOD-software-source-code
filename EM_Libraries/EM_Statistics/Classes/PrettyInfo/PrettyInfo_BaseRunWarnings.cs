﻿using EM_Common;

namespace EM_Statistics
{
    public static partial class PrettyInfoProvider
    {
        private class PrettyInfo_BaseRunWarnings : PrettyInfo
        {
            protected override string ident { get => PRETTY_INFO_BASE_RUN_WARNINGS; }

            internal override string ReplaceText(string origText, PrettyInfoResources resources)
            {
                return resources.baseSystems != null && resources.baseSystems.Count > 0 ?
                    (resources.baseSystems[0].GetFileGenesis(out SystemInfo.FileGenesis fileGenesis) ?
                    origText.Replace(ident, PrettyInfoFileGenesis.GetPrettyErrLog(fileGenesis)) : origText.Replace(ident, DefPar.Value.NA)) : origText;
            }
        }
    }
}
