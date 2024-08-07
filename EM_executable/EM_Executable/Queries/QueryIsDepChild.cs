﻿using System.Collections.Generic;
using EM_Common;

namespace EM_Executable
{
    internal class QueryIsDepChild : QueryBase
    {
        internal QueryIsDepChild(InfoStore infoStore) : base(infoStore) { }

        internal override void CheckAndPrepare(FunBase fun, List<string> footnoteNumbers) {}

        internal override double GetValue(HH hh, List<Person> tu, Person person)
        {
            return person.isDepChild ? 1.0 : 0.0;
        }
    }
}
